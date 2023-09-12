from sqlalchemy import Boolean, ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    balance = Column(Integer, default=0)
    is_restricted = Column(Boolean(), default=False)
    buy = relationship('Buy', back_populates='user')
    borrow = relationship('Borrow', back_populates='user')


class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    daily_borrow_fee = Column(Integer)
    max_borrow_amount = Column(Integer)
    book = relationship('Book', back_populates='category')


class Book(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    category_name = Column(String, ForeignKey('category.name'))
    category = relationship('Category', back_populates='book')
    stock_amount = Column(Integer)
    salable_quantity = Column(Integer)
    price = Column(Integer)
    buy = relationship('Buy', back_populates='book')
    borrow = relationship('Borrow', back_populates='book')


class Buy(Base):
    id = Column(Integer, primary_key=True, index=True)
    bought_date = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='buy')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='buy')


class Borrow(Base):
    id = Column(Integer, primary_key=True, index=True)
    borrowed_date = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    borrow_days = Column(Integer, default=0)
    returned_date = Column(DateTime(timezone=True), default=None, index=True, nullable=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='borrow')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='borrow')
