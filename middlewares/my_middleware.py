from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
from aiogram.types import Message,Update
from typing import *
from data.config import CHANNELS
from loader import bot
from utils.misc.subscription import check
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import os


class CheckSubs(CallbackData,prefix='ikb3'):
    check:bool
class CheckSubsCall(CallbackData,prefix='ikb25'):
    test:str
DEFAULT_RATE_LIMIT = .1
class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        if event.text:
            user_id = event.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        final_status = True
        builder = InlineKeyboardBuilder()
        for CHANNEL in CHANNELS:
            status = await check(user_id=user_id,channel=CHANNEL)
            final_status*=status
            print(status)
            channel = await bot.get_chat(CHANNEL)
            try:
                if status:
                    builder.button(text=f"✅ {channel.title}", url=f"{await channel.export_invite_link()}")
                else:
                    builder.button(text=f"❌ {channel.title}", url=f"{await channel.export_invite_link()}")
            except Exception as e:
                print(e)
                pass
        text = "Obunani tekshirish"
        builder.button(text=text, callback_data=CheckSubs(check=True))
        builder.adjust(1)
        if not final_status:
            await bot.send_message(chat_id=user_id, text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!", reply_markup=builder.as_markup())
        else:
            return await handler(event, data)