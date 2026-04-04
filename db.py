import os 

from pathlib import Path

def get_db_url():
	secret_path = Path("/run/secrets/db-password")
	if secret_path.exists():
		password = secret_path.read_text().strip()
	else:
		password = os.getenv("DB_PASSWORD", default="password")
	
	return f"postgresql+asyncpg://appuser:{password}@db:5432/sec_daily"
	
	
	
