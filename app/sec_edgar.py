# edgartools 
from edgar import set_identity, Company

# Use your name and email (required by SEC)
set_identity("Loy Yeeko koloyyee@gmail.com")

company = Company("AAPL")
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