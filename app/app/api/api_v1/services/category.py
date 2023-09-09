from .... import crud, utils
from .... import exceptions as exc
from ....models import Book


async def get_category_by_book(db, book: Book):
    category = await crud.category.get_by_book(db, book=book)
    if not category:
        raise exc.InternalServiceError(
            status_code=400,
            detail="Error, This book has no category associated with it!",
            msg_code=utils.MessageCodes.bad_request
        )
    return category


async def get_all_categories(db):
    categories = await crud.category.get_multi(db, limit=None)
    return categories
