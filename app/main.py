import asyncio
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from datastar_py.fastapi import (
    DatastarResponse,
    ReadSignals,
    ServerSentEventGenerator,
)
from .sec_edgar import latest_filing_html, filing_links
from .ui import header, root_body

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    # return HTMLResponse(HTML.replace("CURRENT_TIME", f"{datetime.isoformat(datetime.now())}"))
    return HTMLResponse(header(root_body().replace("CURRENT_TIME", f"{datetime.isoformat(datetime.now())}")))


@app.get("/show-msg", response_class=StreamingResponse)
async def show_msg():
    return DatastarResponse(
             ServerSentEventGenerator.patch_elements("<p id='msg'> Dafuq? </p>"))


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
    #print(signals)
    return DatastarResponse(time_updates())


@app.get("/latest/{ticker}/{form}", response_class=HTMLResponse)
async def latest_filing(ticker: str, form: str):
    html = latest_filing_html(ticker, form)
    if html is None:
        return RedirectResponse("/")
    return HTMLResponse(html)


@app.get("/{ticker}/{forms}/")
async def latest_10ks(ticker: str, forms: str = "10-K", latest: int = 3):
    forms = forms.split(",")
    filings = filing_links(ticker, forms=forms, last_n=latest)
    url_trs = "\n".join([f"""\
        <tr> 
            <td> <a href='{f["url"]}' target="_blank">{f["primary_doc"]} </a> </td> 
            <td> {f["filing_date"]:%Y-%m-%d}</td> 
        </tr>
        
        """ for f in filings])
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
