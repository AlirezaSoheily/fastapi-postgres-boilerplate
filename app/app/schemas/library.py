from pydantic import BaseModel
from datetime import datetime
from typing import List
from .user import User


class CategoryBase(BaseModel):
    name: str
    daily_borrow_fee: int
    max_borrow_amount: int


class CategoryCreate(CategoryBase):
    name: str
    daily_borrow_fee: int
    max_borrow_amount: int


class CategoryUpdate(CategoryBase):
    daily_borrow_fee: int
    max_borrow_amount: int


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    title: str
    author: str
    category_name: str
    stock_amount: int
    salable_quantity: int
    price: int


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    stock_amount: int
    salable_quantity: int


class Book(BookBase):
    id: int
    category: Category

    class Config:
        orm_mode = True


class ClientBase(BaseModel):
    balance: int
    is_restricted: bool
    user_id: int


class ClientCreate(ClientBase):
    user_id: int
    balance: int


class ClientUpdate(ClientBase):
    user_id: int
    balance: int
    is_restricted: bool


class Client(ClientBase):
    id: int
    user: User

    # buy: 'Buy'
    # borrow: 'Borrow'

    class Config:
        orm_mode = True


class BuyBase(BaseModel):
    book_id: int
    client_id: int


class BuyCreate(BuyBase):
    pass


class BuyUpdate(BuyBase):
    pass


class Buy(BuyBase):
    id: int
    client: Client
    book: Book

    class Config:
        orm_mode = True


class BorrowBase(BaseModel):
    borrow_days: int
    returned_date: datetime
    book_id: int
    client_id: int


class BorrowCreate(BorrowBase):
    book_id: int
    client_id: int


class BorrowUpdate(BorrowBase):
    borrow_days: int | None = 1
    returned_date: datetime | None = None


class Borrow(BorrowBase):
    id: int
    client: Client
    book: Book

    class Config:
        orm_mode = True
