from sqlalchemy import Table, Boolean, ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.base_class import Base

# Tables for many-to-many relation of user-buy and user-borrow
user_buy_association = Table(
    'user_buy_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('buy_id', Integer, ForeignKey('buy.id'))

)

user_borrow_association = Table(
    'user_borrow_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('borrow_id', Integer, ForeignKey('borrow.id'))

)


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    client = relationship('Client', back_populates='user')
    buy = relationship('Buy', secondary=user_buy_association, back_populates='user')
    borrow = relationship('Borrow', secondary=user_borrow_association, back_populates='user')


class Client(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    user = relationship('User', back_populates='client')
    balance = Column(Integer, default=0)
    is_restricted = Column(Boolean(), default=False)
