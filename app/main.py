import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session
from .db import create_db_and_tables


app = FastAPI()

@app.get("/hello")
def read_root():
    return {"Hello": "World"}
