import asyncio
from collections.abc import AsyncGenerator
import os 

from pathlib import Path
from typing import Annotated
from fastapi import Depends
#from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import text 
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

class Base(DeclarativeBase):
	pass

def _get_db_url():
	secret_path = Path("/run/secrets/db-password")
	if secret_path.exists():
		password = secret_path.read_text().strip()
	else:
		password = os.getenv("DB_PASSWORD", default="password")
	
	host = os.getenv("DB_HOST", default="localhost")
	return f"postgresql+asyncpg://appuser:{password}@{host}:5432/insider-daily"

engine = create_async_engine(_get_db_url(), echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=True)
async def get_async_session() -> AsyncGenerator[AsyncSession]:
	async with AsyncSessionLocal() as session:
		yield session

# Smoke test
if __name__ == "__main__":
	import asyncio
	async def _test():
		async with AsyncSessionLocal() as session:
			result = await session.execute(text("select 'hello world'"))
			print(result.fetchall())

	asyncio.run(_test())

	
	
	
