from ....models import Borrow
from sqlalchemy.ext.asyncio import AsyncSession
from .... import crud
from .user import reduce_from_user_balance
from datetime import datetime, timedelta
import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__file__)


async def get_active_borrow_objects(db: AsyncSession):
    borrows = await crud.borrow.get_active_borrows(db)
    return borrows


async def check_user_violation(db, borrow: Borrow):
    borrowed_date = borrow.borrowed_date
    borrow_days = timedelta(days=borrow.borrow_days)
    today = datetime.now(borrow.borrowed_date.tzinfo)
    if (today - borrowed_date) > borrow_days:
        await reduce_from_user_balance(db, user=borrow.user, reduce_amount=(borrow.book.category.daily_borrow_fee * 5))
        borrow.user.is_restricted = True
        logger.info(f"------user {borrow.user.full_name} got restricted for the book {borrow.book.title} ! -------")


async def reduce_borrow_fee_from_user_balance(borrow_objs, db):
    for borrow in borrow_objs:
        await reduce_from_user_balance(db, user=borrow.user, reduce_amount=borrow.book.category.daily_borrow_fee)
        if not borrow.user.is_restricted:
            await check_user_violation(db, borrow)
