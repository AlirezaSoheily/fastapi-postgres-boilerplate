from typing import Any, Dict, Union, Awaitable
from .. import exceptions as exc
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .crud_user import user
from ..crud.base import CRUDBase
from ..models.user import User, Book, Buy, Borrow, Category
from ..schemas.library import CategoryUpdate, CategoryCreate, BookCreate, BookUpdate, BuyCreate, BuyUpdate, \
    BorrowCreate, BorrowUpdate
from .. import utils
from ..api.api_v1 import services


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

    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Book).filter(Book.title == name)
        return self._first(db.scalars(query))


book = CRUDBook(Book)


class CRUDBuy(CRUDBase[Buy, BuyCreate, BuyUpdate]):
    async def create(self, db: Session | AsyncSession, *, book_name: str, user_email: str) -> Buy:
        book_obj = await book.get_by_name(db, name=book_name)
        user_obj = await user.get_by_email(db, email=user_email)
        book_id = int(str(book_obj).split(':')[-1])
        user_id = int(str(user_obj).split(':')[-1])
        buy_obj = {'book_id': book_id, 'user_id': user_id}
        services.reduce_one_book_from_db(db, book=book_obj)
        services.reduce_from_user_balance(db, user=user_obj, reduce_amount=book_obj.price)
        return await super().create(db, obj_in=buy_obj)


buy = CRUDBuy(Buy)


class CRUDBorrow(CRUDBase[Borrow, BorrowCreate, BorrowUpdate]):
    def get_by_user_and_book(self, db: Session | AsyncSession, *, user: User, book: Book
                             ) -> Borrow:
        query = select(Borrow).filter(Borrow.user == user).filter(Borrow.book == book).filter(
            Borrow.returned_date.is_(None)).last()
        return self._first(db.scalars(query))


borrow = CRUDBorrow(Borrow)
