from datetime import datetime
from typing import List, Any
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..crud.base import CRUDBase
from ..models.user import User, Book, Borrow
from ..schemas.library import BorrowCreate, BorrowUpdate


class CRUDBorrow(CRUDBase[Borrow, BorrowCreate, BorrowUpdate]):
    def get_by_user_and_book(self, db: Session | AsyncSession, *, user: User, book: Book
                             ) -> Borrow:
        query = select(Borrow).filter(Borrow.user == user).filter(Borrow.book == book).filter(
            Borrow.returned_date.is_(None))
        return self._first(db.scalars(query))

    def get_not_returned_borrow_obj_from_user(self, db: Session | AsyncSession, *, user: User) -> List[Borrow]:
        query = select(Borrow).options(
            joinedload(Borrow.book)).filter(Borrow.user_id == user.id).filter(Borrow.returned_date.is_(None))
        return self._all(db.scalars(query))

    def get_borrow_objects_within_a_time_period(self, db: Session | AsyncSession, *, book: Book,
                                                time_period: datetime) -> List[Borrow]:
        query = select(Borrow).filter(Borrow.borrowed_date >= time_period).filter(
            Borrow.book_id == book.id)
        return self._all(db.scalars(query))

    def get_all_user_borrow(self, db: Session | AsyncSession, *, user: User) -> List[Borrow]:
        query = select(Borrow).filter(Borrow.user_id == user.id)
        return self._all(db.scalars(query))

    def get_all_joined(self, db: Session | AsyncSession) -> List[Borrow]:
        query = select(Borrow).options(joinedload(Borrow.book).joinedload(Book.category))
        return self._all(db.scalars(query))

    def get_active_borrows(self, db: Session | AsyncSession) -> Any:
        query = select(Borrow).options(joinedload(Borrow.book).joinedload(Book.category)).options(joinedload(Borrow.user)).filter(Borrow.returned_date.is_(None))
        return self._all(db.scalars(query))

    def book_records(self, db: Session | AsyncSession, book: Book) -> List[Borrow]:
        query = select(Borrow).options(joinedload(Borrow.user)).filter(Borrow.book == book)
        return self._all(db.scalars(query))

    def group_by_books(self, db: Session | AsyncSession) -> Any:
        query = select(Borrow.book_id, Borrow.id, func.count(Borrow.book_id)).group_by(Borrow.book_id, Borrow.id)
        return self._all(db.scalars(query))


borrow = CRUDBorrow(Borrow)
