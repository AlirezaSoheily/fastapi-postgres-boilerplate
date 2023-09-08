from datetime import datetime, timedelta
from typing import Any
from .. import services
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .... import crud, models, schemas, utils
from ....api import deps
from ....utils import APIResponseType, APIResponse
from .... import exceptions as exc
from sqlalchemy.future import select
from ....models import Book, Borrow

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


@router.post('/balance/charge')
async def charge_balance(*, db: AsyncSession = Depends(deps.get_db_async), user_in: schemas.UserUpdateBalance,
                         current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    Charge a user balance by admin.
    """

    user = await services.get_user_by_email(db, user_in.email)
    await services.add_to_user_balance(db, user=user, add_amount=user_in.add_amount)
    return {"user's name": user.full_name, "balance": user.balance}


@router.post('/book')
async def create_book(*, db: AsyncSession = Depends(deps.get_db_async), book_in: schemas.BookCreate,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
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
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    Borrow a book by admin.
    """
    user = await services.get_user_by_email(db, borrow_in.user_email)
    book = await services.get_book_by_name(db, name=borrow_in.book_name)
    services.check_user_restrict(user)
    services.check_book_availability(book_availability=book.stock_amount, book_wanted=1)
    if user.balance < book.price:
        raise exc.InternalServiceError(
            status_code=400,
            detail="Your balance is not enough. Please consider charging your account.",
            msg_code=utils.MessageCodes.bad_request,
        )
    # services.check_user_balance(user.balance, int(book.category.daily_borrow_fee))
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
    borrow_obj.returned_date = datetime.utcnow()
    await db.commit()
    return APIResponse(borrow_obj)


@router.post('/test')
async def test(*, db: AsyncSession = Depends(deps.get_db_async), email: str,
               current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    user = await crud.user.get_by_email(db, email=email)
    all_borrows = await crud.borrow.get_all_user_borrow(db, user=user)
    all_active_borrows = await crud.borrow.get_not_returned_borrow_obj_from_user(db, user=user)
    result = {'all': [], 'not returned': []}
    for borr in all_active_borrows:
        result['active'].append(borr)
    for borrow in all_borrows:
        result['all'].append(borrow)
    return result
