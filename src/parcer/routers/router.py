from aiogram import Router
from .coomand import router as command_router


async def get_routers() -> Router:
    router = Router()
    router.include_router(command_router)
    return router
