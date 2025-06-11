from aiogram import Router
from .coomand import router as main_router
from .data import router as data_router


async def get_routers() -> Router:
    router = Router()
    router.include_router(main_router)
    router.include_router(data_router)

    return router
