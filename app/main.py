import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from .sec_edgar import latest_filing_html,filing_links


app = FastAPI()

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

@app.get("/latest/{ticker}/{form}", response_class=HTMLResponse)
async def latest_filing(ticker : str, form: str):
    html = latest_filing_html(ticker, form)
    return HTMLResponse(html)

@app.get("/{ticker}/{forms}/" )
async def latest_10ks(ticker : str, forms: str = "10-K", latest: int = 3):
    forms = forms.split(",") 
    filings = filing_links(ticker,forms=forms, last_n= latest )
    url_trs = "\n".join([f"""\
        <tr> 
            <td> <a href='{f["url"]}' target="_blank">{f["primary_doc"]} </a> </td> 
            <td> {f["filing_date"]:%Y-%m-%d}</td> 
        </tr>
        
        """ for f in filings])
    return HTMLResponse( f"""\
        <table>
        <thead>
            <th> Link </th>
            <th> Date </th>
        </thead>
            <tbody>
                    {url_trs} 
            </table>
        </tbody>
        """)
    

if __name__ == "__main__":
    uvicorn.run(app)