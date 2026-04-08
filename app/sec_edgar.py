# edgartools 
from edgar import set_identity, Company
from edgar.entity import EntityFiling, EntityFilings
from .ticker_enum import Ticker as T

set_identity("Loy Yeeko koloyyee@gmail.com")

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
	#print(income)
	#print(financials.get_net_income())
	df = financials.income_statement().to_dataframe()
	#print(df.head())

#get_company_financials(T.AAPL.value)
	
# company = Company(str(T.PDD))
# filings = company.get_filings(year=[ 2023, 2024, 2025], form=["20-F", "6-K"])
# print(filings)


def latest_filing_html(ticker: str, form: str) -> str:
  company = Company(ticker)
  latest = company.get_filings(form=form).latest(1)
  if latest is not None:
    return latest.html()

def filing_links(ticker: str, forms:[str], last_n: int = 3) -> [str]:
  company = Company(ticker)
  filings = company.get_filings(form=forms).latest(last_n)
  cik = filings.cik
  filings = filings.to_dict()
  print(filings)
  urls : [str] = []
  for filing in filings:
    access_num = filing["accession_number"].replace("-", "")
    primary_doc = filing["primaryDocument"]
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{access_num}/{primary_doc}"
    urls.append({
			"url": url,
			"form": filing["form"],
			"primary_doc": primary_doc,
			"filing_date": filing["filing_date"]
		})
  return sorted(urls, key = lambda filing_date:  filing["filing_date"])