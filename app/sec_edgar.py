from edgar import set_identity, Company
from edgar.entity import EntityFiling, EntityFilings
from edgar import get_current_filings
from pprint import pprint
import json

set_identity("Loy Yeeko koloyyee@gmail.com")

c = Company("RDDT")

f4s = c.get_filings(form=4).latest(5)
files = [ f.obj()  for f in f4s]
print(files)

def get_company_financials(ticker: str):
  # Use your name and email (required by SEC)
  company = Company(str(ticker))
  print(company)
  print(company.industry)
  financials = company.get_financials()

  # The three financial statements
  income    = financials.income_statement()
  balance   = financials.balance_sheet()
  cashflow  = financials.cashflow_statement()
  print(income)
  print(financials.get_net_income())
  df = financials.income_statement().to_dataframe()
  #print(df.head())

#get_company_financials("HOOD")

#c = Company("HOOD")
#tenq = c.latest_tenq
#b = tenq.financials.balance_sheet()
#print(b)

  
# company = Company(str(T.PDD))
# filings = company.get_filings(year=[ 2023, 2024, 2025], form=["20-F", "6-K"])
# print(filings)


def latest_filing_html(ticker: str, form: str = "10-K") -> str:
  company = Company(ticker)
  latest = company.get_filings(form=form).latest(1)
  if latest is not None:
    return latest.html()

def filing_links(ticker: str, forms: [str], last_n: int = 3) -> [str]:
  company = Company(ticker)
  urls = []
  for form in forms:
    filings = company.get_filings(form=form).latest(last_n)

    if filings is None:
      continue

    cik = filings.cik
    filings_dict = filings.to_dict()
    for filing in filings_dict:
      access_num = filing["accession_number"].replace("-", "")
      primary_doc = filing["primaryDocument"]
      url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{access_num}/{primary_doc}"
      urls.append({
        "url": url,
        "form": filing["form"],
        "primary_doc": primary_doc,
        "filing_date": filing["filing_date"]
      })
  return sorted(urls, key=lambda x: x["filing_date"])


#latest = filing_links("AAPL", ["10-K", "10-Q", "8-K", "13-F"], 5)

#print(len(latest))

#current = get_current_filings().to_dict()
#print(f"Found {len(current)} recent filings")

#pprint(current)
#json.dumps(current, indent=2)

# Display the first few filings
#for filing in current[:5]:
    #print(f"{filing.form}: {filing.company} - {filing.filing_date}")
