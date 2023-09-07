from sqlalchemy.future import select
from ....models import Borrow
from ....utils.schedule import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from ... import deps
from .user import reduce_from_user_balance
from datetime import datetime, timedelta


async def get_active_borrow_objects(db: AsyncSession = Depends(deps.get_db_async)):
    active_borrow_objects_query = select(Borrow).filter(Borrow.returned_date.is_(None))
    borrow_objs = await db.execute(active_borrow_objects_query)
    return borrow_objs


async def check_user_violation(db, borrow: Borrow):
    borrowed_date = borrow.borrowed_date
    borrow_days = timedelta(days=borrow.borrow_days)
    today = datetime.utcnow()
    if today - borrowed_date > borrow_days:
        await reduce_from_user_balance(db, user=borrow.user, reduce_amount=(borrow.book.category.daily_borrow_fee * 5))
        borrow.user.is_restricted = True
        logger.info(f"------user {borrow.user.full_name} got restricted for the book {borrow.book.title} ! -------")


async def reduce_borrow_fee_from_user_balance(borrow_objs, db: AsyncSession = Depends(deps.get_db_async)):
    for borrow in borrow_objs:
        await reduce_from_user_balance(db, user=borrow.user, reduce_amount=borrow.book.category.daily_borrow_fee)
        if not borrow.user.is_restricted:
            await check_user_violation(db, borrow)
