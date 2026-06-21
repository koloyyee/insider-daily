from pydantic import BaseModel
from sqlalchemy import String, null
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Company(Base):
	"""
	Company follows the SEC Edgar basic company information.
	"""
	__tablename__ = "companies"
	ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
	cik: Mapped[str] = mapped_column(String(20), nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)

