from aiogram import Router, Bot, F
from aiogram import types
from aiogram.filters import Command, CommandObject
from typing import Optional
import os
from utils.product_categorize import ProductManager
from utils.database_helper import db_helper

router = Router()

DOWNLOAD_DIR = "data"


text = """
/help: Помощь по командам.
/format: Отформатировать файл и определить категории и подкатегории товаров. Вместе с командой отправить файл excel.
/database: Занеси данные из отправленного excel файла в базуданных. Аргументы: override - если нужно перезаписать уже существующие данные.
Пример:
/database override - Отправляется вместе с файлом excel и перезапишет все найденные записи в бд на основе данного файла.
/database - Занесет только новые записи.
"""


@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply(text)


@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(text)


async def upload_file_to_server(
    bot: Bot,
    file_id: str,
    original_file_name: str,
    user_id: int,
    message_id: int,
) -> Optional[str]:
    if not os.path.exists(DOWNLOAD_DIR):
        try:
            os.makedirs(DOWNLOAD_DIR)
        except OSError:
            return None
    server_file_name = f"{user_id}_{message_id}_{original_file_name}"
    file_path = os.path.join(DOWNLOAD_DIR, server_file_name)

    try:
        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, destination=file_path)
        return file_path
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        return None


@router.message(Command("format"), F.document)
async def handle_document(message: types.Message, bot: Bot):
    document = message.document
    file_id = document.file_id
    original_file_name = document.file_name or f"unknown_file_{file_id}"
    local_file_path = await upload_file_to_server(
        bot=bot,
        file_id=file_id,
        original_file_name=original_file_name,
        user_id=message.from_user.id,
        message_id=message.message_id,
    )

    if not local_file_path:
        await message.reply(
            "Произошла ошибка при сохранении вашего файла на сервере. Пожалуйста, попробуйте позже."
        )
        return
    try:
        output_file = types.FSInputFile(
            path=local_file_path, filename=original_file_name
        )
        manager = ProductManager(local_file_path)
        manager.to_excel()
        await message.answer_document(
            document=output_file,
            caption=f"Вот ваш обработанный файл: {original_file_name}",
        )

    except Exception as e:
        await message.reply(f"Произошла ошибка при работе с файлом: {e}")
    finally:
        try:
            os.remove(local_file_path)

        except OSError:
            pass


@router.message(Command("database"))
async def parse_file_to_database(
    message: types.Message, bot: Bot, command: CommandObject
):
    # Инициализация переменных
    override = False
    local_file_path = None

    try:
        # Парсинг аргументов команды
        if command.args:
            args = command.args.split()
            override = args[0] == "override"

        # Проверка наличия документа
        if not message.document:
            await message.reply("Пожалуйста, прикрепите файл к команде.")
            return

        document = message.document
        file_id = document.file_id
        original_file_name = document.file_name or f"unknown_file_{file_id}"

        # Загрузка файла на сервер
        local_file_path = await upload_file_to_server(
            bot=bot,
            file_id=file_id,
            original_file_name=original_file_name,
            user_id=message.from_user.id,
            message_id=message.message_id,
        )

        if not local_file_path:
            await message.reply(
                "Произошла ошибка при сохранении вашего файла на сервере. "
                "Пожалуйста, попробуйте позже."
            )
            return

        # Импорт данных в БД
        db_helper.insert_new_data(local_file_path, override=override)
        await message.reply("Данные успешно добавлены в базу данных.")

    except Exception as e:
        await message.reply(f"Произошла ошибка при работе с файлом: {e}")

    finally:
        # Очистка: удаление временного файла
        if local_file_path:
            try:
                os.remove(local_file_path)
            except OSError:
                pass
