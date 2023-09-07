from .... import crud, utils
from .... import exceptions as exc
from ....models import Book


async def get_book_by_name(db, name: str):
    book = await crud.book.get_by_name(db, name=name)
    if not book:
        raise exc.InternalServiceError(
            status_code=400,
            detail="A book with this name does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )
    return book


async def reduce_one_book_from_db(db, book: Book):
    book.stock_amount -= 1
    book.salable_quantity -= 1
    await db.commit()
    return True


def check_book_availability(book_availability: int, book_wanted: int):
    if book_availability < book_wanted:
        raise exc.InternalServiceError(
            status_code=400,
            detail="there is not enough of this book in library.",
            msg_code=utils.MessageCodes.bad_request,
        )
