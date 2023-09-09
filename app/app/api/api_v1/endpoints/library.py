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


@router.post('/book')
async def create_book(*, db: AsyncSession = Depends(deps.get_db_async), book_in: schemas.BookCreate,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    Create new book by admin.
    """
    await services.check_category_existence(db, book=book_in)
    await services.check_book_re_stocking(db, book_in=book_in)
    book = await crud.book.create(db, obj_in=book_in)
    return APIResponse(book)


@router.put('/book/re-stock/{book_name}')
async def create_book(*, db: AsyncSession = Depends(deps.get_db_async), book_name: str, book_in: schemas.BookUpdate,
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> Any:
    """
    re-stock a book by admin.
    """
    book = await services.get_book_by_name(db, name=book_name)
    await services.re_stocking_book(db,book_obj=book ,book_in=book_in)
    return APIResponse(book)


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
