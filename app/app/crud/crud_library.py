from typing import Any, Dict, Union, Awaitable
from .. import exceptions as exc
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload, selectinload
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

    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Book).filter(Book.title == name)
        return self._first(db.scalars(query))


book = CRUDBook(Book)


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    async def create(self, db: Session | AsyncSession, *, user_id: int, email: str) -> Client:
        db_obj = Client(user_id=user_id, email=email)
        db.add(db_obj)
        await db.commit()
        return db_obj

    # Client | None | Awaitable[Client | None]
    def get_by_email(
            self, db: Session | AsyncSession, *, email: str
    ) -> Awaitable[Client | None]:
        return self._first(db.scalars(select(self.model).options(selectinload(self.model.user.email == email))))



        # query = select(Client).join(User).filter(User.email == email)
        # result = await db.execute(query)
        # client_with_email = result.scalar_one_or_none()
        # return client_with_email


client = CRUDClient(Client)


class CRUDBuy(CRUDBase[Buy, BuyCreate, BuyUpdate]):
    async def create(self, db: Session | AsyncSession, *, book_name: str, client_email: str) -> Buy:
        book_obj = await book.get_by_name(db, name=book_name)
        client_obj = await client.get_by_email(db, email=client_email)
        book_id = int(str(book_obj).split(':')[-1])
        client_id = int(str(client_obj).split(':')[-1])
        buy_obj = {'book_id': book_id, 'client_id': client_id}
        book_obj.salable_quantity -= 1
        book_obj.stock_amount -= 1
        client_obj.balance -= book_obj.price
        await db.commit()
        return await super().create(db, obj_in=buy_obj)


buy = CRUDBuy(Buy)


class CRUDBorrow(CRUDBase[Borrow, BorrowCreate, BorrowUpdate]):
    ...


borrow = CRUDBorrow(Borrow)
