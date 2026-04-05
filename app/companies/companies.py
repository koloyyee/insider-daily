import json
from pathlib import Path
import os
from enum import Enum
import io
import time
import httpx


def is_old_file(file_path: Path, days: int):
	m_dt = file_path.stat().st_mtime
	return (time.time() - m_dt) > (days * 24 * 60 * 60)


def get_companies(force_update: bool = False):
	clean_path = Path("app/companies/companies.json")

	if not os.path.exists(clean_path) or is_old_file(clean_path, 90) or force_update:
		print("Pulling from company tickers from SEC...")
		sec_companies_json_url = "https://www.sec.gov/files/company_tickers.json"
		latest_companies_json = httpx.get(sec_companies_json_url, headers={
    		"User-Agent": "Loyyee Ko koloyyee@gmail.com",
		}).json()

		with open(clean_path, "w") as f:
			companies = list(latest_companies_json.values())
			json.dump(companies, f, indent=4)
			return companies
	else:
		with open(clean_path, "r") as f:
			companies = json.load(f)
			return companies

def generate_ticker_enum():
	ticker_enum = Path("app/ticker_enum.py")
	with open(ticker_enum, "w") as f:
		companies = get_companies()
		buffer = io.StringIO()
		for c in companies:
			if "-" in c['ticker']:
				buffer.write(f"{c['ticker'].replace("-", "_")} = {c['cik_str']}\n\t")
			else:
				buffer.write(f"{c['ticker']} = {c['cik_str']}\n\t")
		body = f"""
from enum import Enum

class Ticker(Enum):
	{buffer.getvalue()}

	def __str__(self) -> str:
		return self.name.replace("_", "-")
	"""
		f.write(body)

generate_ticker_enum()