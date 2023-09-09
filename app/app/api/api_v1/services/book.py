from .... import crud, utils
from .... import exceptions as exc
from ....models import Book
from ....schemas import BookCreate, BookUpdate


async def check_category_existence(db, book: BookCreate):
    categories = await crud.category.get_multi(db, limit=None)
    for category in categories:
        if book.category_name == category.name:
            return True
    raise exc.InternalServiceError(
        status_code=404,
        detail="This category does not exist.",
        msg_code=utils.MessageCodes.not_found,
    )


async def check_book_re_stocking(db, book_in: BookCreate):
    books = await crud.book.get_multi(db, limit=None)
    for book in books:
        if book_in.title == book.title:
            raise exc.InternalServiceError(
                status_code=400,
                detail=f"A book with the name {book_in.title} exist in the system, Try re-stocking service.",
                msg_code=utils.MessageCodes.bad_request
            )


async def re_stocking_book(db, book_obj: Book, book_in: BookUpdate):
    book_obj.stock_amount += book_in.stock_amount
    book_obj.salable_quantity += book_in.salable_quantity
    await db.commit()


async def get_book_by_name(db, name: str):
    book = await crud.book.get_by_name(db, name=name)
    if not book:
        raise exc.InternalServiceError(
            status_code=400,
            detail="A book with this name does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )
    return book


async def reduce_one_book_from_db(db, book_: Book):
    book_.stock_amount -= 1
    book_.salable_quantity -= 1
    await db.commit()
    return True


def check_book_availability(book_availability: int, book_wanted: int):
    if book_availability < book_wanted:
        raise exc.InternalServiceError(
            status_code=400,
            detail="there is not enough of this book in library.",
            msg_code=utils.MessageCodes.bad_request,
        )


async def get_category_by_name(db, name: str):
    category_ = await crud.category.get_by_name(db, name=name)
    if not category_:
        raise exc.InternalServiceError(
            status_code=400,
            detail="A category with this name does not exist in the system.",
            msg_code=utils.MessageCodes.bad_request
        )
    return category_


async def get_all_saleable_books(db):
    books = await crud.book.get_saleable_books(db)
    return books
