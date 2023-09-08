from datetime import datetime, timedelta

from .... import crud, utils
from .... import exceptions as exc
from ....models import Book, User


async def get_borrow_with_user_and_book(db, user: User, book: Book):
    borrow_obj = await crud.borrow.get_by_user_and_book(db, user=user, book=book)
    if not borrow_obj:
        raise exc.InternalServiceError(
            status_code=400,
            detail="A borrow record with this user and book does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )


async def check_if_user_borrowed_max_amount_from_category(db, user: User, book: Book):
    borrow_objs = await crud.borrow.get_not_returned_borrow_obj_from_user(db, user=user)
    category_count = 0
    for borrow in borrow_objs:
        borrow_obj = borrow[0]
        if borrow_obj.book.category_name == book.category_name:
            category_count += 1
    if category_count >= book.category.max_borrow_amount:
        raise exc.InternalServiceError(
            status_code=400,
            detail="You have borrowed too much from this category of book, please consider borrowing a book with "
                   "another category.",
            msg_code=utils.MessageCodes.bad_request,
        )


async def calculate_max_allowed_borrow_days(db, book: Book):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    borrow_obj = await crud.borrow.get_borrow_objects_within_a_time_period(db, book=book, time_period=thirty_days_ago)
    time_period_borrow_count = 0
    for borrow in borrow_obj:
        time_period_borrow_count += 1
    max_borrow_days_allowed = ((30 * book.stock_amount) // (book.stock_amount + time_period_borrow_count)) + 1
    if max_borrow_days_allowed < 3:
        max_borrow_days_allowed = 3
    return max_borrow_days_allowed
