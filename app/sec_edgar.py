# edgartools 
from edgar import set_identity, Company
from ticker_enum import Ticker as T

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
	
company = Company(str(T.PDD))
filings = company.get_filings(year=[ 2023, 2024, 2025], form=["20-F", "6-K"])
print(filings)