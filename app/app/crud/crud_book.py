from typing import Awaitable
from .crud_category import category
from .. import exceptions as exc
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..crud.base import CRUDBase
from ..models.user import Book
from ..schemas.library import BookCreate, BookUpdate
from .. import utils


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

    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Book).filter(Book.title == name)
        return self._first(db.scalars(query))


book = CRUDBook(Book)
