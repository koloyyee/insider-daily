# Pydantic Schemas

from datetime import date
from pydantic import BaseModel


class FilingInfo(BaseModel):
    """Raw data extracted from an RSS entry."""
    date: str
    cik: str
    acc_no: str
    title: str
    link: str
    updated: str


class TransactionSummary(BaseModel):
    """A single transaction inside a Form 4."""
    transaction_type: str  # purchase, sale, award, exercise, gift, etc.
    shares: int
    value: float | None
    price_per_share: float | None
