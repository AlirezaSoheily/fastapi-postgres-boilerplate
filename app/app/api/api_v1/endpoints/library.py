from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from .... import crud, models, schemas, utils
from ....api import deps
from ....utils import APIResponseType, APIResponse
from .... import exceptions as exc

from cache import cache, invalidate
from cache.util import ONE_DAY_IN_SECONDS

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
                      current_user: models.User = Depends(deps.get_current_active_admin)) -> APIResponseType[
    schemas.Book]:
    """
    Create new book by admin.
    """

    book = await crud.book.create(db, book_in=book_in)
    return APIResponse(book)
