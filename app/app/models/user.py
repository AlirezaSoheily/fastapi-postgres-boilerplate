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
