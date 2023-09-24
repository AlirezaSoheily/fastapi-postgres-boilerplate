from typing import Any, List
from sqlalchemy import func
from . import book

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .crud_user import user
from ..crud.base import CRUDBase
from ..models import Book, Buy, User
from ..schemas.library import BuyCreate, BuyUpdate
from ..api.api_v1 import services


class CRUDBuy(CRUDBase[Buy, BuyCreate, BuyUpdate]):
    async def create(self, db: Session | AsyncSession, *, book_obj: Book, user_obj: User) -> Buy:
        book_id = book_obj.id
        user_id = user_obj.id
        buy_obj = {'book_id': book_id, 'user_id': user_id}
        return await super().create(db, obj_in=buy_obj)

    def get_all_joined(self, db: Session | AsyncSession) -> List[Buy]:
        query = select(Buy).options(joinedload(Buy.book).joinedload(Book.category))
        return self._all(db.scalars(query))

    def group_by_books(self, db: Session | AsyncSession) -> Any:
        query = select(Buy.book_id, Buy.id, func.count(Buy.book_id)).group_by(Buy.book_id, Buy.id)
        return self._all(db.scalars(query))


buy = CRUDBuy(Buy)
