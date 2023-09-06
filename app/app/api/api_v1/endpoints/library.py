from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .... import crud, models, schemas, utils
from ....api import deps
from ....models import Client, User, Book, Category, Borrow
from ....utils import APIResponseType, APIResponse
from .... import exceptions as exc
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
async def update_balance(*, db: AsyncSession = Depends(deps.get_db_async), client_in: schemas.ClientUpdateBalance,
                         current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Client]:
    """
    Update a client balance by admin.
    """
    query = select(Client).filter(Client.email == client_in.email)
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    if not client:
        pass
    client.balance += client_in.add_amount
    await db.commit()
    return APIResponse(client)


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
                   current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Buy]:
    """
    Buy a book by admin.
    """
    query = select(Client).filter(Client.email == buy_in.client_email)
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    if not client:
        pass
    book = await crud.book.get_by_name(db, name=buy_in.book_name)
    if not book:
        pass
    if client.balance >= book.price:
        if book.salable_quantity > 0:
            if not client.is_restricted:
                buy_obj = await crud.buy.create(db, book_name=buy_in.book_name, client_email=buy_in.client_email)
                return APIResponse(buy_obj)
            else:
                raise exc.InternalServiceError(
                    status_code=400,
                    detail="you are restricted and you cant buy this book.",
                    msg_code=utils.MessageCodes.permisionError,
                )
        else:
            raise exc.InternalServiceError(
                status_code=400,
                detail="there is not enough of this book in library.",
                msg_code=utils.MessageCodes.bad_request,
            )
    else:
        raise exc.InternalServiceError(
            status_code=400,
            detail="Your balance is not enough to buy this book, please consider charging your account.",
            msg_code=utils.MessageCodes.bad_request,
        )


@router.post('/book/borrow')
async def borrow_book(*, db: AsyncSession = Depends(deps.get_db_async), borrow_in: schemas.BorrowIn,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Borrow]:
    """
    Borrow a book by admin.
    """
    client_query = select(Client).filter(Client.email == borrow_in.client_email)
    result1 = await db.execute(client_query)
    client = result1.scalar_one_or_none()
    book_query = select(Book).filter(Book.title == borrow_in.book_name)
    result2 = await db.execute(book_query)
    book = result2.scalar_one_or_none()
    category_query = select(Category).filter(Category.name == book.category_name)
    result3 = await db.execute(category_query)
    category = result3.scalar_one_or_none()
    borrow_query = select(Borrow).filter(Borrow.client_id == client.id).filter(Borrow.returned_date.is_(None))
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
    last_30_days_query = select([func.count()]).filter(Borrow.borrowed_date >= thirty_days_ago).filter(
        Borrow.book_id == book.id)
    result_last_30 = await db.execute(last_30_days_query)
    last_30_days_borrow_count = result_last_30.scalar()
    max_borrow_days_allowed = ((30 * book.stock_amount) // (book.stock_amount + last_30_days_borrow_count)) + 1
    if max_borrow_days_allowed < 3:
        max_borrow_days_allowed = 3
    if client.balance < category.daily_borrow_fee * 3:
        raise exc.InternalServiceError(
            status_code=400,
            detail="Your balance is not enough to borrow this book.Please consider charging your account.",
            msg_code=utils.MessageCodes.bad_request,
        )

    borrow = crud.borrow.create(dbو )


@router.post('/test')
async def test(*, db: AsyncSession = Depends(deps.get_db_async), buy_in: schemas.BuyIn,
               current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Client]:
    client = crud.client.get_by_email(db, email=buy_in.client_email)
    return client
