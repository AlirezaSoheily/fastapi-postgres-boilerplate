from fastapi import APIRouter

from ...api.api_v1.endpoints import users, utils, library, services

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(library.router, prefix="/library", tags=["library"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
