from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..crud.base import CRUDBase
from ..models.user import Category
from ..schemas.library import CategoryUpdate, CategoryCreate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session | AsyncSession, *, name: str
                    ):
        query = select(Category).filter(Category.name == name)
        return self._first(db.scalars(query))


category = CRUDCategory(Category)
