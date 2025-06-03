from aiogram import Router, Bot
from aiogram import types
from aiogram.filters import Command
import os
from utils.product_categorize import ProductManager

from utils.upload import upload_file_to_server

router = Router()


text = """
/help: Помощь по командам.
/format: Отформатировать файл и определить категории и подкатегории товаров. Вместе с командой отправить файл excel.
/database: Занеси данные из отправленного excel файла в базуданных. Аргументы: override - если нужно перезаписать уже существующие данные.
Пример:
/database override - Отправляется вместе с файлом excel и перезапишет все найденные записи в бд на основе данного файла.
/database - Занесет только новые записи.

/get: Получить актуальные данные из базы данных.
"""


@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply(text)


@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(text)


@router.message(Command("format"))
async def handle_document(message: types.Message, bot: Bot):
    # Инициализация переменных
    local_file_path = None

    try:
        if not message.document:
            await message.reply("Пожалуйста, прикрепите файл к команде.")
            return

        # Загрузка файла на сервер
        local_file_path, original_file_name = await upload_file_to_server(
            bot=bot,
            message=message,
        )

        if not local_file_path:
            await message.reply(
                "Произошла ошибка при сохранении вашего файла на сервере. "
                "Пожалуйста, попробуйте позже."
            )
            return
        # Обработка файла
        manager = ProductManager(local_file_path)
        manager.to_excel()

        # Поиск пустых категорий
        empty_rows = manager.find_empty_category()
        empty_rows_message = (
            f"\nНе удалось определить категории товаров на позициях: {empty_rows}"
            if empty_rows
            else "\nВсе категории были успешно определены."
        )

        # Подготовка и отправка обработанного файла
        output_file = types.FSInputFile(
            path=local_file_path, filename=f"processed_{original_file_name}"
        )

        await message.answer_document(
            document=output_file,
            caption=(
                "Обработанный файл."
                f"{empty_rows_message}"
                "\n\nУбедительная просьба проверить корректность определения категорий, "
                "результат может отличаться от действительности."
            ),
        )

    except Exception as e:
        await message.reply(
            f"Произошла ошибка при обработке файла: {e}\n"
            "Пожалуйста, попробуйте еще раз или обратитесь к администратору."
        )

    finally:
        # Очистка: удаление временного файла
        if local_file_path and os.path.exists(local_file_path):
            try:
                os.remove(local_file_path)
            except OSError:
                pass
