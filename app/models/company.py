from pydantic import BaseModel
from sqlalchemy import String, null
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Company(Base):
	__tablename__ = "companies"
	cik: Mapped[str] = mapped_column(String(20), primary_key=True)
	ticker: Mapped[str] = mapped_column(String(10),unique=True, nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)