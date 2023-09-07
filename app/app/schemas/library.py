from pydantic import BaseModel, EmailStr
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


# class ClientBase(BaseModel):
#     email: EmailStr | None = None
#     balance: int
#     is_restricted: bool
#     user_id: int
#
#
# class ClientCreate(ClientBase):
#     user_id: int
#     balance: int = 0
#
#
# class ClientUpdate(ClientBase):
#     user_id: int
#     balance: int
#     is_restricted: bool
#
#
# class ClientUpdateBalance(BaseModel):
#     email: EmailStr
#     add_amount: int
#
# class Client(ClientBase):
#     id: int
#     user: User
#
#     # buy: 'Buy'
#     # borrow: 'Borrow'
#
#     class Config:
#         orm_mode = True


class BuyBase(BaseModel):
    book_id: int | None
    user_id: int | None


class BuyCreate(BaseModel):
    pass


class BuyIn(BaseModel):
    book_name: str | None
    user_email: EmailStr | None


class BuyUpdate(BuyBase):
    pass


class Buy(BuyBase):
    id: int
    user: User | None
    book: Book | None

    class Config:
        orm_mode = True


class BorrowBase(BaseModel):
    borrow_days: int
    returned_date: datetime
    book_id: int
    user_id: int


class BorrowCreate(BaseModel):
    book_id: int
    user_id: int
    borrow_days: int


class BorrowIn(BaseModel):
    book_name: str
    user_email: EmailStr


class BorrowUpdate(BorrowBase):
    borrow_days: int | None
    returned_date: datetime | None


class Borrow(BorrowBase):
    id: int
    user: User
    book: Book

    class Config:
        orm_mode = True


class BookSaleabilityReport(BaseModel):
    pass