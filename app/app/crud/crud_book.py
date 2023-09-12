from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..crud.base import CRUDBase
from ..models.user import Book
from ..schemas.library import BookCreate, BookUpdate


class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):

    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Book).filter(Book.title == name)
        return self._first(db.scalars(query))

    def get_saleable_books(self, db: Session | AsyncSession):
        query = select(Book).filter(Book.salable_quantity > 0)
        return self._all(db.scalars(query))


book = CRUDBook(Book)
