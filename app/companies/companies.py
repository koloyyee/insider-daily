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
	sec_companies_json_url = "https://www.sec.gov/files/company_tickers.json"

	raw_path = Path("app/companies/raw_companies.json")
	clean_path = Path("app/companies/companies.json")

	if is_old_file(raw_path, 7) or force_update:
		latest_companies_json = httpx.get(sec_companies_json_url).json()
		with open(raw_path, "w") as f:
			json.dump(latest_companies_json, f, indent=4)

	companies = [] 

	if os.path.exists(clean_path) and os.path.getsize(clean_path) == 0:
		with open (raw_path, "r") as f:
			data = json.load(f)
			companies = list(data.values())
			print(companies)

		with open(clean_path, "w") as f:
			json.dump(companies, f, indent=4)
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
				buffer.write(f" {c['ticker'].replace("-", "_")} = {c['cik_str']}\n\t")
			else:
				buffer.write(f" {c['ticker']} = {c['cik_str']}\n\t")
		body = f"""
	from enum import Enum

	class Ticker(Enum):
		{buffer.getvalue()}
		"""
		f.write(body)
