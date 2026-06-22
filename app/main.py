import asyncio
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import (
    DatastarResponse,
    ReadSignals,
    ServerSentEventGenerator,
)

from app.services import stream_form4
from .sec_edgar import latest_filing_html, filing_links
from .ui import header, main_body, form4_row

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    # return HTMLResponse(header(root_body().replace("CURRENT_TIME", f"{datetime.isoformat(datetime.now())}")))
    return HTMLResponse(header(main_body()))


@app.get("/show-msg", response_class=StreamingResponse)
async def show_msg():
    return DatastarResponse(
        ServerSentEventGenerator.patch_elements("<p id='msg'> Dafuq? </p>")
    )


async def time_updates():
    while True:
        yield ServerSentEventGenerator.patch_elements(
            f"""<span id="currentTime">{datetime.now().isoformat()}"""
        )
        await asyncio.sleep(1)
        yield ServerSentEventGenerator.patch_signals(
            {"currentTime": f"{datetime.now().isoformat()}"}
        )
        await asyncio.sleep(1)


@app.get("/updates", response_class=StreamingResponse)
async def updates(signals: ReadSignals):
    # ReadSignals is a dependency that automatically loads the signals from the request
    # print(signals)
    return DatastarResponse(time_updates())


@app.get("/form4", response_class=StreamingResponse)
async def list_latest_form4():
    return DatastarResponse(_stream_form4_rows())


async def _stream_form4_rows():
    """Yields Datastar SSE patches — one row per filing as they arrive."""
    async for item in stream_form4():
        if item is None:
            # Cache hit — instant replay from cache, just as fast
            continue
        yield ServerSentEventGenerator.patch_elements(
            form4_row(item),
            selector="#form4_feed",
            mode=ElementPatchMode.APPEND,
        )


@app.get("/company/{ticker}", response_class=HTMLResponse)
async def company_detail(ticker: str):
    """Show the latest Form 4 filing HTML for a company."""
    html = latest_filing_html(ticker, "4")
    if html is None:
        return HTMLResponse(
            header(
                f"<p class='text-gray-500 mt-8'>No Form 4 filings found for {ticker}.</p>"
            )
        )
    return HTMLResponse(
        header(f"""\
<h1 class='font-bold text-2xl mb-4'>{ticker.upper()} — Latest Form 4</h1>
<div class="max-w-full overflow-auto border border-gray-200 rounded-lg p-2">
  {html}
</div>
<p class="mt-4"><a href="/" class="text-blue-500 hover:text-blue-700 underline">&larr; Back to feed</a></p>
""")
    )


@app.get("/latest/{ticker}/{form}", response_class=HTMLResponse)
async def latest_filing(ticker: str, form: str):
    html = latest_filing_html(ticker, form)
    if html is None:
        return RedirectResponse("/")
    return HTMLResponse(html)


@app.get("/{ticker}/{forms}/")
async def latest_10ks(ticker: str, forms: str = "10-K", latest: int = 3):
    _forms = forms.split(",")
    filings = filing_links(ticker, forms=_forms, last_n=latest)
    url_trs = "\n".join(
        [
            f"""\
        <tr> 
            <td> <a href='{f["url"]}' target="_blank">{f["primary_doc"]} </a> </td> 
            <td> {f["filing_date"]:%Y-%m-%d}</td> 
        </tr>
        
        """
            for f in filings
        ]
    )
    body = f"""\
        <table>
            <thead>
                <th> Link </th>
                <th> Date </th>
            </thead>
            <tbody>
                {url_trs} 
            </tbody>
        </table>
        """
    return HTMLResponse(header(body))


if __name__ == "__main__":
    uvicorn.run(app)
