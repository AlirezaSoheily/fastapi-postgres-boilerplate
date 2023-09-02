from sqlalchemy import Table, Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime

from .user import user_buy_association, user_borrow_association
from ..db.base_class import Base


class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    daily_borrow_fee = Column(Integer)
    max_borrow_amount = Column(Integer)
    books = relationship('Book', back_populates='category')


# Tables for many-to-many relation of book-buy and book-borrow
book_buy_association = Table(
    'book_buy_association',
    Base.metadata,
    Column('buy_id', Integer, ForeignKey('buy.id')),
    Column('book_id', Integer, ForeignKey('book.id'))
)

book_borrow_association = Table(
    'book_borrow_association',
    Base.metadata,
    Column('borrow_id', Integer, ForeignKey('borrow.id')),
    Column('book_id', Integer, ForeignKey('book.id'))
)


class Book(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category', back_populates='book')
    stock_amount = Column(Integer)
    salable_quantity = Column(Integer)
    price = Column(Integer)
    buy = relationship('Buy', secondary=book_buy_association, back_populates='book')
    borrow = relationship('Borrow', secondary=book_borrow_association, back_populates='book')


class Buy(Base):
    id = Column(Integer, primary_key=True, index=True)
    bought_date = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    book = relationship('Book', secondary=book_buy_association, back_populates='buy')
    user = relationship('User', secondary=user_buy_association, back_populates='buy')


class Borrow(Base):
    id = Column(Integer, primary_key=True, index=True)
    borrowed_date = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    borrow_days = Column(Integer, default=0)
    returned_date = Column(DateTime(timezone=True), index=True)
    book = relationship('Book', secondary=book_borrow_association, back_populates='borrow')
    user = relationship('User', secondary=user_borrow_association, back_populates='borrow')
