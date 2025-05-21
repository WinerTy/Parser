from aiogram import Router, F, Bot
from aiogram import types
import os
from utils.product_categorize import ProductManager

router = Router()

DOWNLOAD_DIR = "data"
# @router.message()
# async def echo_handler(message: types.Message) -> None:
#     """
#     Handler will forward received message back to the sender

#     By default, message handler will handle all message types (like text, photo, sticker and etc.)
#     """
#     try:
#         if message.document:
#             doc_id = message.document.file_id
#             await message.answer_document(doc_id)
#         # Send copy of the received message
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")


@router.message(F.document)
async def handle_document(message: types.Message, bot: Bot):
    if not message.document:
        await message.reply("Пожалуйста, отправьте файл.")
        return
    document = message.document
    file_id = document.file_id
    original_file_name = document.file_name or "unknown_file"

    if not os.path.exists(DOWNLOAD_DIR):
        try:
            os.makedirs(DOWNLOAD_DIR)
        except OSError:
            await message.reply(
                "Ошибка сервера: не удалось создать папку для сохранения файла."
            )
            return
    server_file_name = (
        f"{message.from_user.id}_{message.message_id}_{original_file_name}"
    )
    local_file_path = os.path.join(DOWNLOAD_DIR, server_file_name)

    try:
        await message.reply(f"Получен файл: {original_file_name}. Скачиваю...")

        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, destination=local_file_path)

        await message.answer(
            f"Файл '{original_file_name}' успешно сохранен на сервере."
        )
        input_file = types.FSInputFile(
            path=local_file_path, filename=original_file_name
        )
        manager = ProductManager(local_file_path)
        manager.to_exsel()
        await message.answer_document(
            document=input_file, caption=f"Вот ваш файл обратно: {original_file_name}"
        )

    except Exception as e:
        await message.reply(f"Произошла ошибка при работе с файлом: {e}")
    finally:
        try:
            os.remove(local_file_path)

        except OSError:
            pass
