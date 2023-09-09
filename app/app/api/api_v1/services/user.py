from datetime import timedelta, datetime
from typing import List

from .... import crud, utils
from .... import exceptions as exc
from ....models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from ... import deps


async def get_user_by_email(db, email):
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise exc.InternalServiceError(
            status_code=400,
            detail="The user with this email does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )
    return user


def check_user_balance(user_balance: int, price: int):
    if user_balance < price:
        raise exc.InternalServiceError(
            status_code=400,
            detail="Your balance is not enough. Please consider charging your account.",
            msg_code=utils.MessageCodes.bad_request,
        )


def check_user_restrict(user: User):
    if user.is_restricted:
        raise exc.InternalServiceError(
            status_code=400,
            detail="you are restricted and you can't buy or borrow this book.",
            msg_code=utils.MessageCodes.permisionError,
        )


async def get_restricted_users(db: AsyncSession = Depends(deps.get_db_async)):
    restricted_users = await crud.user.get_restricted_users(db)
    return restricted_users


async def un_restrict_users(users: List[User], db: AsyncSession = Depends(deps.get_db_async)):
    for user in users:
        for borrow in user.borrow:
            days = timedelta(days=borrow.borrow_days)
            if datetime.utcnow() > (borrow.borrowed_date + days):
                if not borrow.returned_date:
                    return None
        user.is_restricted = False
        await db.commit()


async def get_violated_users(db):
    users = await crud.user.get_all_users_joined(db)
    violations = {}
    for user in users:
        for borrow in user.borrow:
            days = timedelta(days=borrow.borrow_days)
            now = datetime.now(borrow.borrowed_date.tzinfo)
            if borrow.returned_date:
                if borrow.returned_date > (borrow.borrowed_date + days):
                    user_has_dict_key = violations.get(user.email, None)
                    if not user_has_dict_key:
                        violations[user.email] = [borrow]
                    else:
                        violations[user.email].append(borrow)
            else:
                if now > (borrow.borrowed_date + days):
                    user_has_dict_key = violations.get(user.email, None)
                    if not user_has_dict_key:
                        violations[user.email] = [borrow]
                    else:
                        violations[user.email].append(borrow)
    sorted_dict = {k: v for k, v in sorted(violations.items(), key=lambda x: len(x[1]))}
    return sorted_dict


async def get_a_user_violations(db, email):
    user = await crud.user.get_user_by_email_eager(db, email=email)
    violations = []
    for borrow in user.borrow:
        days = timedelta(days=borrow.borrow_days)
        now = datetime.now(borrow.borrowed_date.tzinfo)
        if borrow.returned_date:
            if borrow.returned_date > (borrow.borrowed_date + days):
                violations.append(borrow)
        else:
            if now > (borrow.borrowed_date + days):
                violations.append(borrow)
    return violations


async def reduce_from_user_balance(db, user: User, reduce_amount: int):
    user.balance -= reduce_amount
    await db.commit()
    return True


async def add_to_user_balance(db, user: User, add_amount: int):
    user.balance += add_amount
    await db.commit()
    return True
