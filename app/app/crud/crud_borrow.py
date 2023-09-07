from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..crud.base import CRUDBase
from ..models.user import User, Book, Borrow
from ..schemas.library import BorrowCreate, BorrowUpdate


class CRUDBorrow(CRUDBase[Borrow, BorrowCreate, BorrowUpdate]):
    def get_by_user_and_book(self, db: Session | AsyncSession, *, user: User, book: Book
                             ) -> Borrow:
        query = select(Borrow).filter(Borrow.user == user).filter(Borrow.book == book).filter(
            Borrow.returned_date.is_(None)).last()
        return self._first(db.scalars(query))


borrow = CRUDBorrow(Borrow)
