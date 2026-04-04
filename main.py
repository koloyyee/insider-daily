import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session

# 1. Database Connection Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:password@db:5432/sec_daily")
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Dependency for database sessions
def get_session():
    with Session(engine) as session:
        yield session
