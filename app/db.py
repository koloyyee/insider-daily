import os 

from pathlib import Path
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session

def get_db_url():
	secret_path = Path("/run/secrets/db-password")
	if secret_path.exists():
		password = secret_path.read_text().strip()
	else:
		password = os.getenv("DB_PASSWORD", default="password")
	
	return f"postgresql+asyncpg://appuser:{password}@db:5432/sec_daily"

engine = create_engine(get_db_url())

def create_db_and_tables():
	SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

	
	
	
