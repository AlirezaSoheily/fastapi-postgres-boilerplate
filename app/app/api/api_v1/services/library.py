from .... import crud, models, schemas, utils
from .... import exceptions as exc
from ....models import Book, User


async def get_user_by_email(db, email):
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise exc.InternalServiceError(
            status_code=400,
            detail="The user with this email does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )
    return user


async def get_book_by_name(db, name: str):
    book = await crud.book.get_by_name(db, name=name)
    if not book:
        raise exc.InternalServiceError(
            status_code=400,
            detail="A book with this name does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )
    return book


def check_user_balance(user_balance: int, price: int):
    if user_balance < price:
        raise exc.InternalServiceError(
            status_code=400,
            detail="Your balance is not enough. Please consider charging your account.",
            msg_code=utils.MessageCodes.bad_request,
        )


async def reduce_one_book_from_db(db, book: Book):
    book.stock_amount -= 1
    book.salable_quantity -= 1
    await db.commit()
    return True


def check_user_restrict(user: User):
    if user.is_restricted:
        raise exc.InternalServiceError(
            status_code=400,
            detail="you are restricted and you can't buy or borrow this book.",
            msg_code=utils.MessageCodes.permisionError,
        )


def check_book_availability(book_availability: int, book_wanted: int):
    if book_availability < book_wanted:
        raise exc.InternalServiceError(
            status_code=400,
            detail="there is not enough of this book in library.",
            msg_code=utils.MessageCodes.bad_request,
        )


async def reduce_from_user_balance(db, user: User, reduce_amount: int):
    user.balance -= reduce_amount
    await db.commit()
    return True


async def add_to_user_balance(db, user: User, add_amount: int):
    user.balance += add_amount
    await db.commit()
    return True
