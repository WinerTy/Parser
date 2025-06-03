from aiogram import Bot


from typing import Tuple, Optional

from core import conf

import os

from aiogram.types import Message


def validate_dir() -> bool:
    """Validate and create download directory if needed."""
    if not os.path.exists(conf.upload.dowloand_dir):
        try:
            os.makedirs(conf.upload.dowloand_dir)
            return True
        except OSError as e:
            print(f"Failed to create directory: {e}")
            return False
    return True


async def upload_file_to_server(
    bot: Bot,
    message: Message,
) -> Optional[Tuple[str, str]]:
    """Upload file to server and return (file_path, original_name) or None."""
    if not validate_dir():
        return None

    document = message.document
    if not document:
        return None

    file_id = document.file_id
    original_file_name = document.file_name or f"unknown_file_{file_id}"
    server_file_name = (
        f"{message.from_user.id}_{message.message_id}_{original_file_name}"
    )
    file_path = os.path.join(conf.upload.dowloand_dir, server_file_name)

    try:
        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, destination=file_path)
        return file_path, original_file_name
    except Exception as e:
        print(f"File download failed: {e}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Failed to remove temp file: {e}")
        return None
