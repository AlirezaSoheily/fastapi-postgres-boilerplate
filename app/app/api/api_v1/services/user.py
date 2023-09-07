from .... import crud, utils
from .... import exceptions as exc
from ....models import User


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


async def reduce_from_user_balance(db, user: User, reduce_amount: int):
    user.balance -= reduce_amount
    await db.commit()
    return True


async def add_to_user_balance(db, user: User, add_amount: int):
    user.balance += add_amount
    await db.commit()
    return True
