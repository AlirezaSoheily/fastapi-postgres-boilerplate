from typing import Any, Dict, Union, Awaitable
from .. import exceptions as exc
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..crud.base import CRUDBase
from ..models.user import User, Book, Buy, Client, Borrow, Category
from ..schemas.library import CategoryUpdate, CategoryCreate, BookCreate, BookUpdate, BuyCreate, BuyUpdate, \
    BorrowCreate, BorrowUpdate, ClientCreate, ClientUpdate
from .. import utils


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Category).filter(Category.name == name)
        return self._first(db.scalars(query))


category = CRUDCategory(Category)


class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    async def create(
            self, db: Session | AsyncSession, *, book_in: BookCreate
    ) -> Book | Awaitable[Book]:
        categories = await category.get_multi(db, limit=None)
        for obj in categories:
            if book_in.category_name == obj.name:
                return await super().create(db, obj_in=book_in)
        else:
            raise exc.InternalServiceError(
                status_code=404,
                detail="This category does not exist.",
                msg_code=utils.MessageCodes.not_found,
            )


book = CRUDBook(Book)


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    async def create(self, db: Session | AsyncSession, *, user_id: int) -> Client:
        db_obj = Client(user_id=user_id)
        db.add(db_obj)
        await db.commit()
        return db_obj


client = CRUDClient(Client)


class CRUDBuy(CRUDBase[Buy, BuyCreate, BuyUpdate]):
    ...


buy = CRUDBuy(Buy)


class CRUDBorrow(CRUDBase[Borrow, BorrowCreate, BorrowUpdate]):
    ...


borrow = CRUDBorrow(Borrow)
