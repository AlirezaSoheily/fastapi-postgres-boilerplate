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

router = APIRouter()
namespace = "services"


@router.post('/check_book_saleability')
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
