from uuid import uuid4
from keyboards.inline.buttons import buttons
import sqlite3
from utils.notify_admins import users_count
from loader import dp, bot
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from utils.misc.subscription import check
from data.config import CHANNELS
from aiogram.filters.callback_data import CallbackData
from contextlib import closing


def get_db_connection():
    return sqlite3.connect('bot.db')


class CheckSubs(CallbackData, prefix='ikb3'):
    check: bool


@dp.message(CommandStart())
async def start(message: types.Message):
    """
    Handle the /start command. Check if the user is in the database and subscribed to required channels.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Check if the user is already in the database
    with closing(get_db_connection()) as con:
        cursor = con.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                (user_id, username, full_name),
            )
            con.commit()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            await users_count(user_id, username, full_name, user_count)

    btn = InlineKeyboardBuilder()
    final_status = True
    for channel in CHANNELS:
        status = True
        try:
            status = await check(user_id=user_id, channel=channel['channel_id'])
        except Exception as e:
            print(f"Error checking subscription for channel {channel['channel_id']}: {e}")
            status = False

        final_status *= status
        try:
            channel = await bot.get_chat(channel['channel_id'])
        except Exception as e:
            print(f"Error getting chat for channel {channel['channel_id']}: {e}")
            continue

        if not status:
            try:
                invite_link = await channel.export_invite_link()
                btn.row(InlineKeyboardButton(text=f"❌ {channel.title}", url=invite_link))
            except Exception as e:
                print(f"Error exporting invite link for channel {channel['channel_id']}: {e}")

    btn.button(text="Obunani tekshirish", callback_data=CheckSubs(check=True))
    btn.adjust(1)

    if final_status:
        await message.answer(f'Assalamu Aleykum {full_name}, botimizga xush kelibsiz\nKino kodini kiriting!')
    else:
        await message.answer(
            text="Iltimos, bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
            reply_markup=btn.as_markup(row_width=1)
        )


@dp.message()
async def start_bot(message: types.Message):

    number = message.text
    try:
        await bot.copy_message(chat_id=message.chat.id, from_chat_id="@testcuhun", message_id=number,
                               reply_markup=buttons(film_id=number))
    except Exception as e:
        print(f"Error copying message: {e}")
        await message.answer("Bu kinoni topa olmadim yoki xatolik yuz berdi.")


@dp.callback_query(lambda query: query.data.startswith('delete'))
async def delete_msg(callback_query: types.CallbackQuery):
    """
    Handle callback queries that start with 'delete' and delete the corresponding message.
    """
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.inline_query()
async def inline_handler(inline_query: types.InlineQuery):
    """
    Handle inline queries and respond with video results.
    """
    try:
        film_id = int(inline_query.query)
        message_url = f"https://t.me/testcuhun/{film_id}"
        result = types.InlineQueryResultVideo(
            id=str(uuid4()),
            title="Videoni do'stlarga yuborish",
            video_url=message_url,
            description=f"ID: {film_id}",
            thumbnail_url='https://t.me/ulugbekhusain/49',
            mime_type='video/mp4',
            caption="@aiogram2629_bot"
        )

        await bot.answer_inline_query(
            inline_query.id,
            results=[result],
            cache_time=10,
            is_personal=True,
            switch_pm_parameter="add",
            switch_pm_text="Botga o'tish"
        )
    except Exception as e:
        print(f"Error handling inline query: {e}")


@dp.callback_query(CheckSubs.filter())
async def test(call: types.CallbackQuery):
    """
    Handle callback queries to check subscription status and send update messages.
    """
    await call.answer(cache_time=60)
    buttons_list = []
    final_status = False
    user_id = call.from_user.id

    for kanal in CHANNELS:
        try:
            channel = await bot.get_chat(kanal['channel_id'])
            res = await bot.get_chat_member(chat_id=kanal['channel_id'], user_id=user_id)
            if res.status in ('member', 'administrator', 'creator'):
                buttons_list.append(
                    InlineKeyboardButton(text=f"✅ {channel.title}", url=f"{await channel.export_invite_link()}"))
            else:
                buttons_list.append(
                    InlineKeyboardButton(text=f"❌ {channel.title}", url=f"{await channel.export_invite_link()}"))
                final_status = True
        except Exception as e:
            print(f"Error checking subscription for channel {kanal['channel_id']}: {e}")

    builder = InlineKeyboardBuilder()
    builder.add(*buttons_list)
    builder.button(text="Obunani tekshirish", callback_data=CheckSubs(check=True))
    builder.adjust(1)

    if final_status:
        await bot.send_message(chat_id=user_id,
                               text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
                               reply_markup=builder.as_markup())
    else:
        await call.message.answer(text="Botning sizning xizmatingizda!")
    await call.message.delete()
