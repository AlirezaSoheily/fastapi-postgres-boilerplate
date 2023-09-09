from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..crud.base import CRUDBase
from ..models.user import Category, Book
from ..schemas.library import CategoryUpdate, CategoryCreate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Category).filter(Category.name == name)
        return self._first(db.scalars(query))

    def get_by_book(self, db: Session | AsyncSession, *, book: Book
                    ):
        query = select(Category).filter(Category.name == book.category_name)
        return self._first(db.scalars(query))


category = CRUDCategory(Category)
