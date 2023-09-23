from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime


class Buy(Base):
    id = Column(Integer, primary_key=True, index=True)
    bought_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='buy')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='buy')


class Borrow(Base):
    id = Column(Integer, primary_key=True, index=True)
    borrowed_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    borrow_days = Column(Integer, default=0)
    returned_date = Column(DateTime(timezone=True), default=None, nullable=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='borrow')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='borrow')
