from typing import Any, List
from sqlalchemy import func
from . import book

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .crud_user import user
from ..crud.base import CRUDBase
from ..models import Book, Buy
from ..schemas.library import BuyCreate, BuyUpdate
from ..api.api_v1 import services


class CRUDBuy(CRUDBase[Buy, BuyCreate, BuyUpdate]):
    async def create(self, db: Session | AsyncSession, *, book_name: str, user_email: str) -> Buy:
        book_obj = await book.get_by_name(db, name=book_name)
        user_obj = await user.get_by_email(db, email=user_email)
        book_id = int(str(book_obj).split(':')[-1])
        user_id = int(str(user_obj).split(':')[-1])
        buy_obj = {'book_id': book_id, 'user_id': user_id}
        await services.reduce_one_book_from_db(db, book_=book_obj)
        await services.reduce_from_user_balance(db, user=user_obj, reduce_amount=book_obj.price)
        return await super().create(db, obj_in=buy_obj)

    def get_all_joined(self, db: Session | AsyncSession) -> List[Buy]:
        query = select(Buy).options(joinedload(Buy.book).joinedload(Book.category))
        return self._all(db.scalars(query))

    def group_by_books(self, db: Session | AsyncSession) -> Any:
        query = select(Buy.book_id, Buy.id, func.count(Buy.book_id)).group_by(Buy.book_id, Buy.id)
        return self._all(db.scalars(query))


buy = CRUDBuy(Buy)
