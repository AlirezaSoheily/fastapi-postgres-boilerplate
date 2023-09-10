from datetime import datetime, timedelta
from typing import Any
from .. import services
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .... import crud, models, schemas, utils
from ....api import deps
from pydantic import EmailStr
from ....models import Book, Borrow
from ....utils import APIResponseType, APIResponse
from .... import exceptions as exc
from cache import cache
from cache.util import ONE_DAY_IN_SECONDS

router = APIRouter()
namespace = "services"


@router.post('/check_book_saleability')
async def buy_book(*, db: AsyncSession = Depends(deps.get_db_async), buy_in: schemas.BuyIn,
                   current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    check if this user can buy this book and check the availability of the book by admin.
    """
    user = await services.get_user_by_email(db, buy_in.user_email)
    book = await services.get_book_by_name(db, name=buy_in.book_name)
    services.check_user_restrict(user)
    services.check_user_balance(user_balance=user.balance, price=book.price)
    services.check_book_availability(book_availability=book.salable_quantity, book_wanted=1)
    return {'Congrats!': 'You can buy this book!'}


@router.get('/saleable_books')
async def saleable_books(
        db: AsyncSession = Depends(deps.get_db_async),
        current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    get all saleable books by admin.
    """
    books = await services.get_all_saleable_books(db)
    return books


@router.get('/profit')
@cache(namespace=namespace, expire=ONE_DAY_IN_SECONDS)
async def profit_from_categories(*, db: AsyncSession = Depends(deps.get_db_async),
                                 current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    check the profits each category made by admin.
    """
    borrows = await services.get_all_borrow_objects_joined(db)
    buys = await services.get_all_buy_objects(db)
    categories = await services.get_all_categories(db)
    category_profits = services.calculate_categories_profit(borrows=borrows, buys=buys, categories=categories)
    return category_profits


@router.get('/get_violated_users')
async def get_violated_users(*, db: AsyncSession = Depends(deps.get_db_async)
                             , user_email: EmailStr | None = None,
                             current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    get the violation from users by admin.
    """
    if user_email:
        user_violations = await services.get_a_user_violations(db, email=user_email)
        violations = {user_email: user_violations}
    else:
        violations = await services.get_violated_users(db)
    return violations


@router.post('/book/buy')
async def buy_book(*, db: AsyncSession = Depends(deps.get_db_async), buy_in: schemas.BuyIn,
                   current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    Buy a book by admin.
    """
    user = await services.get_user_by_email(db, buy_in.user_email)
    book = await services.get_book_by_name(db, name=buy_in.book_name)
    services.check_user_restrict(user)
    services.check_user_balance(user_balance=user.balance, price=book.price)
    services.check_book_availability(book_availability=book.salable_quantity, book_wanted=1)
    buy_obj = await crud.buy.create(db, book_name=buy_in.book_name, user_email=buy_in.user_email)
    return APIResponse(buy_obj)


@router.post('/book/borrow')
async def borrow_book(*, db: AsyncSession = Depends(deps.get_db_async), borrow_in: schemas.BorrowIn,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    Borrow a book by admin.
    """
    user = await services.get_user_by_email(db, borrow_in.user_email)
    book = await services.get_book_by_name(db, name=borrow_in.book_name)
    category = await services.get_category_by_book(db, book=book)
    services.check_user_restrict(user)
    services.check_book_availability(book_availability=book.stock_amount, book_wanted=1)
    services.check_user_balance(user.balance, category.daily_borrow_fee * 3)
    await services.check_if_user_borrowed_max_amount_from_category(db, user=user, book=book)
    max_borrow_days_allowed = await services.calculate_max_allowed_borrow_days(db, book=book)
    borrow_dict = {'book_id': book.id, 'user_id': user.id, 'borrow_days': max_borrow_days_allowed}
    borrow = await crud.borrow.create(db, obj_in=borrow_dict)
    await services.reduce_one_book_from_db(db, book)
    return APIResponse(borrow)


@router.post('/book/return')
async def return_book(*, db: AsyncSession = Depends(deps.get_db_async), borrow_in: schemas.BorrowIn,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    user = await services.get_user_by_email(db, borrow_in.user_email)
    book = await services.get_book_by_name(db, name=borrow_in.book_name)
    borrow_obj = await services.get_borrow_with_user_and_book(db, user=user, book=book)
    await services.return_book(db, borrow=borrow_obj)
    return APIResponse(borrow_obj)


@router.get('/book_borrow_records')
async def book_borrow_records(*, db: AsyncSession = Depends(deps.get_db_async)
                              , book_name: str,
                              current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    get a book's borrow records by admin.
    """
    book = await services.get_book_by_name(db, name=book_name)
    records = await services.get_a_book_borrow_records(db, book=book)
    return records


@router.get('/borrow_group_by_books')
async def borrow_group_by_books(*, db: AsyncSession = Depends(deps.get_db_async),
                                current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    get a book's borrow records grouped by books by admin.
    """
    result = await services.get_borrows_group_by_books(db)
    count_dict = services.count_occurrences_of_unique_values(result)
    answer = await services.get_books_names(db, count_dict)
    return answer


@router.get('/buy_group_by_books')
async def buys_group_by_books(*, db: AsyncSession = Depends(deps.get_db_async),
                              current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    get a book's buys records grouped by books by admin.
    """
    result = await services.get_buys_group_by_books(db)
    count_dict = services.count_occurrences_of_unique_values(result)
    answer = await services.get_books_names(db, count_dict)
    return answer
