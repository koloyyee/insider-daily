import asyncio
from datetime import date
from os import access
import feedparser
import re
import time
from concurrent.futures import ThreadPoolExecutor

from edgar import Filing
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Company as Company_Model, Insider as Insider_Model, Filing as Filing_Model, Transaction as Transaction_Model
 



# Simple in-memory cache: {cache_key: (timestamp, data)}
_cache: dict[str, tuple[float, list[dict]]] = {}
CACHE_TTL_SECONDS = 60  # Re-fetch every 60 seconds at most


def filing_info(entry):
    date_pattern = r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}\b"
    acc_no_pattern = r"\b[0-9]{10}-[0-9]{2}-[0-9]{6}\b"
    date = re.findall(date_pattern, entry.summary)[0] if re.findall(date_pattern, entry.summary) else ""
    acc_no = re.findall(acc_no_pattern, entry.summary)[0] if re.findall(acc_no_pattern, entry.summary) else ""
    title = entry.title
    opening = title.find("(")
    closing = title.find(")")
    cik = title[opening + 1 : closing]
    link = entry.link
    return {"date": date, "cik": cik, "acc_no": acc_no, "title": title, "link": link, "updated": entry.updated}


def extract_title(full_title: str) -> str:
    """
    from:
      4 - Atlas Lithium Corp (0001540684) (Issuer)
    to:
      Atlas Lithium Corp
    """
    dash_idx = full_title.find("-")
    first_open = full_title.find("(")
    return full_title[dash_idx + 1 : first_open]


def _fetch_one(entry) -> dict | None:
    """Fetch a single filing's summary. Returns None on failure."""
    try:
        comp_entry = filing_info(entry)
        filing = Filing(
            company=str(comp_entry["cik"]),
            cik=comp_entry["cik"],
            form="4",
            filing_date=comp_entry["date"],
            accession_no=comp_entry["acc_no"],
        )
        f4 = filing.obj()  # type: ignore[assignment]
        xml_display_format = "xslF345X06"
        filing_url = filing.filing_url
        last_slash_idx = filing_url.rfind("/")
        url = filing_url[:last_slash_idx] + "/" + xml_display_format + filing_url[last_slash_idx:]

        return {
            "transaction_summary": f4.get_ownership_summary(), # type: ignore
            "filing_url": url,
            "accession_no": comp_entry["acc_no"],
            "cik": comp_entry["cik"],
            "title": comp_entry["title"]
        }
    except Exception:
        return None


async def stream_form4(n: int = 20):
    """Async generator yielding (result_dict) as each filing arrives, and None for cache-hit shortcut."""
    FORM4_RSS = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=4&company=&dateb=&owner=only&start=0&count={n * 2}&output=atom"
    feedparser.USER_AGENT = "dko@gmail.com"
    now = time.time()

    # Check cache
    cached = _cache.get("latest_form4")
    if cached and (now - cached[0]) < CACHE_TTL_SECONDS:
        yield None  # signal: use cache
        for item in cached[1][:n]:
            yield item
        return

    # Fetch RSS (blocking I/O — offload to thread)
    loop = asyncio.get_running_loop()
    feed = await loop.run_in_executor(None, lambda: feedparser.parse(FORM4_RSS))
    filtered = [entry for entry in feed.entries if "Reporting" not in entry.title]

    # Fetch filings in parallel, yield as each completes
    summaries = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [loop.run_in_executor(pool, _fetch_one, entry) for entry in filtered]
        for coro in asyncio.as_completed(futures):
            result = await coro
            if result is not None:
                summaries.append(result)
                yield result

    # Sort for cache (next load will be instant)
    summaries.sort(key=lambda s: s["transaction_summary"].reporting_date, reverse=True)
    _cache["latest_form4"] = (now, summaries)

async def fetch_and_store_f4(n : int = 30):
    """
    Fetch latest Form 4 filings from SEC and persist to DB.
    """
    FORM4_RSS = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=4&company=&dateb=&owner=only&start=0&count={n * 2}&output=atom"
    feedparser.USER_AGENT = "dko@gmail.com"
    loop = asyncio.get_running_loop()
    feed = await loop.run_in_executor(None, lambda: feedparser.parse(FORM4_RSS))
    filtered = [entry for entry in feed.entries if "Reporting" not in entry.title]

    raw = []
    with ThreadPoolExecutor(max_workers= 10) as pool:
        futures = [loop.run_in_executor(pool, _fetch_one, e) for e in filtered]
        for coro in asyncio.as_completed(futures):
            result = await coro
            if result is not None:
                raw.append(result)
        stored = 0
        async with AsyncSessionLocal() as session:
            for item in raw:
                ts = item["transaction_summary"]
                ticker = ts.issuer_ticker
                if not ticker:
                    continue
                accession_no = item.get("accession_no")
                if await session.get(Filing_Model, accession_no):
                    continue # already stored

                # Upsert company stub
                if not await session.get(Company_Model, ticker.upper()):
                    session.add(Company_Model(
                        ticker=ticker.upper(),
                        cik=item.get("cik", ""),
                        title=item.get("title"))) 
                # Upsert insider
                insider = (await session.execute(
                    select(Insider_Model)
                    .where(Insider_Model.name == ts.insider_name))).scalar_one_or_none()
                if not insider:
                    insider = Insider_Model(name = ts.insider_name)
                    session.add(insider)
                    await session.flush()

                filing = Filing_Model(
                    accession_no = accession_no,
                    ticker = ticker.upper(),
                    insider_id = insider.id,
                    filing_date = date.fromisoformat(ts.reporting_date) if isinstance(ts.reporting_date, str) else ts.reporting_date,
                    filing_url = item["filing_url"] 
                )
                session.add(filing)
                await session.flush()

                for t in ts.transactions:
                    session.add(Transaction_Model(
                        filing_id = accession_no,
                        transaction_type = t.transaction_type,
                        shares = t.shares,
                        value = t.value,
                        price_per_share = t.price_per_share
                    ))
                stored += 1
            await session.commit()
        print(f"fetch_and_store_f4: stored {stored} new filings") # FIX: replace with logging
        return stored
