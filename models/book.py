# models/book.py
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1)
    author: str = Field(index=True, min_length=1)
    isbn: str = Field(unique=True, index=True, min_length=10, max_length=13)
    published_year: int = Field(ge=1000, le=2026)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

class BookCreate(SQLModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    isbn: str = Field(min_length=10, max_length=13)
    published_year: int = Field(ge=1000, le=2026)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    available: bool = Field(default=True)

class BookUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    published_year: Optional[int] = Field(None, ge=1000, le=2026)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    available: Optional[bool] = None