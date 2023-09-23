from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.base_class import Base


class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    daily_borrow_fee = Column(Integer)
    max_borrow_amount = Column(Integer)
    book = relationship('Book', back_populates='category')


class Book(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    category_name = Column(String, ForeignKey('category.name'))
    category = relationship('Category', back_populates='book')
    stock_amount = Column(Integer)
    salable_quantity = Column(Integer)
    price = Column(Integer)
    buy = relationship('Buy', back_populates='book')
    borrow = relationship('Borrow', back_populates='book')
