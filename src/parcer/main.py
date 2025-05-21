from core import conf
from aiogram import Dispatcher, Bot

from routers import get_routers


async def main() -> None:
    bot = Bot(token=conf.bot.token)
    dp = Dispatcher()
    dp.include_routers(await get_routers())
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
