from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Company(Base):
	"""
	Company follows the SEC Edgar basic company information.
	"""
	__tablename__ = "companies"
	ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
	cik: Mapped[str] = mapped_column(String(20), nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)

class Insider(Base):
	"""
	Insider (person/organisation) as reporter of a SEC filing.
	"""
	__tablename__ = "insiders"
	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(255), nullable = False)

class Filing(Base):
	"""
	SEC filing
	"""
	__tablename__ = "filings"

	accession_no : Mapped[str] = mapped_column(String(30), primary_key=True)
	ticker: Mapped[str] = mapped_column(String(10), ForeignKey("companies.ticker"), nullable=False)
	insider_id: Mapped[int | None] = mapped_column(ForeignKey("insiders.id"))
	filing_date: Mapped[date] = mapped_column(Date, nullable=False)
	filing_url: Mapped[str] = mapped_column(String(500))
	transactions: Mapped[list["Transaction"]] = relationship(back_populates="filing")

class Transaction(Base):
	__tablename__ = "transactions"

	id: Mapped[int] = mapped_column(primary_key=True)
	filing_id: Mapped[str] = mapped_column(ForeignKey("filings.accession_no"), nullable=False)
	transaction_type: Mapped[str] = mapped_column(String(20))
	shares: Mapped[int] = mapped_column(Integer)
	value: Mapped[float | None] = mapped_column(Float)
	price_per_share: Mapped[float | None]  = mapped_column(Float)

	filing: Mapped[Filing] = relationship(back_populates="transactions")
