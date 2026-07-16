# main.py
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query, status
from sqlmodel import Session, select, or_

from database.session import get_session, init_db
from models.book import Book, BookCreate, BookUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Book Inventory API", version="1.0.0", lifespan=lifespan)

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(Book).where(Book.isbn == book_in.isbn)).first()
    if existing:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists")
    
    db_book = Book(**book_in.dict())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.get("/books", response_model=List[Book])
def list_books(
    skip: int = 0,
    limit: int = 10,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    query = select(Book)
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    if min_price is not None:
        query = query.where(Book.price >= min_price)
    if max_price is not None:
        query = query.where(Book.price <= max_price)
    if available is not None:
        query = query.where(Book.available == available)
        
    return session.exec(query.offset(skip).limit(limit)).all()

@app.get("/books/search", response_model=List[Book])
def search_books(q: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    query = select(Book).where(
        or_(
            Book.title.ilike(f"%{q}%"),
            Book.author.ilike(f"%{q}%")
        )
    )
    return session.exec(query).all()

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    update_data = book_update.dict(exclude_unset=True)
    
    if "isbn" in update_data and update_data["isbn"] != db_book.isbn:
        existing = session.exec(select(Book).where(Book.isbn == update_data["isbn"])).first()
        if existing:
            raise HTTPException(status_code=400, detail="A book with this ISBN already exists")

    for key, value in update_data.items():
        setattr(db_book, key, value)
        
    db_book.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(db_book)
    session.commit()
    return None