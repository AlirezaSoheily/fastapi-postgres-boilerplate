from datetime import datetime, timedelta
from typing import Any
from .. import services
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .... import crud, models, schemas, utils
from ....api import deps
from ....models import Book, Borrow
from ....utils import APIResponseType, APIResponse
from .... import exceptions as exc
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from cache import cache, invalidate
from cache.util import ONE_DAY_IN_SECONDS

router = APIRouter()
namespace = "library"


@router.post('/category')
async def create_category(*, db: AsyncSession = Depends(deps.get_db_async), category_in: schemas.CategoryCreate,
                          current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Category]:
    """
    Create new category by admin.
    """
    category = await crud.category.get_by_name(db, name=category_in.name)
    if category:
        raise exc.InternalServiceError(
            status_code=400,
            detail="This category with this name already exists in the system.",
            msg_code=utils.MessageCodes.bad_request,
        )
    category = await crud.category.create(db, obj_in=category_in)
    return APIResponse(category)


@router.post('/balance')
async def update_balance(*, db: AsyncSession = Depends(deps.get_db_async), user_in: schemas.UserUpdateBalance,
                         current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.User]:
    """
    Update a user balance by admin.
    """

    user = await services.get_user_by_email(db, user_in.email)
    await services.add_to_user_balance(db, user=user, add_amount=user_in.add_amount)
    return APIResponse(user)


@router.post('/book')
async def create_book(*, db: AsyncSession = Depends(deps.get_db_async), book_in: schemas.BookCreate,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Book]:
    """
    Create new book by admin.
    """

    book = await crud.book.create(db, book_in=book_in)
    return APIResponse(book)


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
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Borrow]:
    """
    Borrow a book by admin.
    """
    user = await services.get_user_by_email(db, borrow_in.user_email)
    book = await services.get_book_by_name(db, name=borrow_in.book_name)
    services.check_user_restrict(user)
    services.check_book_availability(book_availability=book.stock_amount, book_wanted=1)
    category = await crud.category.get_by_name(name=book.category_name)
    services.check_user_balance(user.balance, category.daily_borrow_fee * 3)
    borrow_query = select(Borrow).filter(Borrow.user_id == user.id).filter(Borrow.returned_date.is_(None))
    borrow_history = await db.execute(borrow_query)
    category_count = 0
    for borrow in borrow_history:
        borrow_obj = borrow[0]
        book_query2 = select(Book).filter(Book.id == borrow_obj.book_id)
        result2 = await db.execute(book_query2)
        book = result2.scalar_one_or_none()
        if book.category_name == category.name:
            category_count += 1
    if category_count >= category.max_borrow_amount:
        raise exc.InternalServiceError(
            status_code=400,
            detail="You have borrowed too much from this category of book, please consider borrowing from another "
                   "category.",
            msg_code=utils.MessageCodes.bad_request,
        )
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    last_30_days_query = select(Borrow).filter(Borrow.borrowed_date >= thirty_days_ago).filter(
        Borrow.book_id == book.id)
    result_last_30 = await db.execute(last_30_days_query)
    last_30_days_borrow_count = 0
    for obj in result_last_30:
        last_30_days_borrow_count += 1
    max_borrow_days_allowed = ((30 * book.stock_amount) // (book.stock_amount + last_30_days_borrow_count)) + 1
    if max_borrow_days_allowed < 3:
        max_borrow_days_allowed = 3

    # if user.balance < category.daily_borrow_fee * 3:
    #     raise exc.InternalServiceError(
    #         status_code=400,
    #         detail="Your balance is not enough to borrow this book.Please consider charging your account.",
    #         msg_code=utils.MessageCodes.bad_request,
    #     )
    borrow_dict = {'book_id': book.id, 'user_id': user.id, 'borrow_days': max_borrow_days_allowed}
    borrow = await crud.borrow.create(db, obj_in=borrow_dict)
    await services.reduce_one_book_from_db(db, book)
    # book.stock_amount -= 1
    # book.salable_quantity -= 1
    # await db.commit()
    return APIResponse(borrow)


@router.post('/book/return')
async def return_book(*, db: AsyncSession = Depends(deps.get_db_async), borrow_in: schemas.BorrowIn,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Borrow]:
    user = await services.get_user_by_email(db, borrow_in.user_email)
    book = await services.get_book_by_name(db, name=borrow_in.book_name)
    borrow_obj = await crud.borrow.get_by_user_and_book(user=user, book=book)
    borrow_obj.returned_date = datetime.utcnow()
    await db.commit()
    return APIResponse(borrow_obj)


@router.post('/book/check_saleability')
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
    return {'Congrats!': 'You can buy this book!'}


@router.post('/test')
async def test(*, db: AsyncSession = Depends(deps.get_db_async), buy_in: schemas.BuyIn,
               current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.User]:
    user = await crud.user.get_by_email(db, email=buy_in.user_email)
    return APIResponse(user)
