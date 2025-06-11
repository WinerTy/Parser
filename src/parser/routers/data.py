from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandObject
from utils.database_helper import db_helper
from core import conf
import os
from datetime import datetime
from utils.upload import upload_file_to_server

router = Router()


@router.message(Command("get"))
async def get_actual_data(
    message: types.Message,
):
    file_path = None
    try:
        data = db_helper.get_actual_data()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"actual_data_{timestamp}.xlsx"
        file_path = os.path.join(conf.upload.dowloand_dir, file_name)

        # Save to Excel
        data.to_excel(file_path, index=False)

        # Send document
        await message.reply_document(
            document=types.FSInputFile(path=file_path, filename=file_name),
            caption=f"Актуальные данные на {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )

    except Exception as e:
        await message.reply(f"Произошла ошибка при получении данных: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass


@router.message(Command("update"))
async def update_data(message: types.Message, bot: Bot):
    # Инициализация переменных
    local_file_path = None

    local_file_path, original_file_name = await upload_file_to_server(
        bot=bot,
        message=message,
    )

    db_helper.update_data(local_file_path)
    await message.reply("Данные успешно обновлены в базе данных.")


@router.message(Command("database"))
async def parse_file_to_database(
    message: types.Message, bot: Bot, command: CommandObject
):
    # Инициализация переменных
    override = False
    local_file_path = None

    try:
        if command.args:
            args = command.args.split()
            override = args[0] == "override"

        if not message.document:
            await message.reply("Пожалуйста, прикрепите файл к команде.")
            return

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

        db_helper.insert_new_data(local_file_path, override=override)
        await message.reply("Данные успешно добавлены в базу данных.")

    except Exception as e:
        await message.reply(f"Произошла ошибка при работе с файлом: {e}")

    finally:
        if local_file_path:
            try:
                os.remove(local_file_path)
            except OSError:
                pass
