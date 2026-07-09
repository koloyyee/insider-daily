import asyncio
import logging
from datetime import date
from os import access
import feedparser
import re
import time
from concurrent.futures import ThreadPoolExecutor

from edgar import Filing

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import AsyncSessionLocal
from app.models import Company as Company_Model, Insider as Insider_Model, Filing as Filing_Model, Transaction as Transaction_Model
 


logger = logging.getLogger(__name__)

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
            "title": comp_entry["title"],
            "filing_date": comp_entry["date"],
        }
    except Exception as e:
        logger.warning("_fetch_one failed for %s: %s", getattr(entry, "title", "?"), e)
        return None

async def retrieve_form4(n: int =20) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Filing_Model)
            .options(
                joinedload(Filing_Model.company),
                joinedload(Filing_Model.insider),
                joinedload(Filing_Model.transactions),
            )
            .order_by(Filing_Model.filing_date.desc())
            .limit(n)
        )
        filings = result.unique().scalars().all()
    rows = []
    for f in filings:
        transactions = []
        net_shares = 0
        total_value = 0
        for t in f.transactions:
            transactions.append({
                "transaction_type" : t.transaction_type,
                "shares": t.shares,
                "value": t.value,
                "price_per_share": t.price_per_share
            })
            if t.transaction_type in ("purchase", "award"):
                net_shares += t.shares
            elif t.transaction_type in ("sale"):
                net_shares -= t.shares
            if t.value:
                total_value += t.value
        rows.append({
            "ticker": f.ticker or "?",
            "company_name" : f.company.title if f.company else f.ticker,
            "insider_name" : f.insider.name if f.insider else "Unknown",
            "filing_date" : str(f.filing_date),
            "filing_url": f.filing_url,
            "net_shares": net_shares,
            "total_value": total_value
        })
    return rows

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
                    filing_date = date.fromisoformat(item["filing_date"]),
                    filing_url = item["filing_url"]
                )
                session.add(filing)
                await session.flush()

                for t in ts.transactions:
                    def _to_float(v):
                        if v is None or isinstance(v, (int, float)):
                            return v
                        cleaned = v.replace(",", "")
                        try:
                            return float(cleaned)
                        except ValueError:
                            return None
                    pps = _to_float(t.price_per_share)
                    val = _to_float(t.value)
                    session.add(Transaction_Model(
                        filing_id = accession_no,
                        transaction_type = t.transaction_type,
                        shares = t.shares,
                        value = val,
                        price_per_share = pps
                    ))
                stored += 1
            await session.commit()
        logger.info("fetch_and_store_f4: stored %s new filings", stored)
        return stored
