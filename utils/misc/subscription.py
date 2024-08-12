from typing import Union
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from loader import bot


async def check(user_id: int, channel: Union[str, int]) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)

        if member.status in ['member', 'administrator', 'creator', 'restricted']:
            print(member.status)
            return True
        else:
            return False
    except TelegramBadRequest as e:
        print(f"Failed to check membership status: {e}")
        return False
