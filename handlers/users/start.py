from uuid import uuid4
from aiogram.filters import CommandStart
from keyboards.inline.buttons import buttons
from loader import dp, bot
from aiogram import types
import sqlite3
from data.config import ADMINS
from utils.notify_admins import users_count
con = sqlite3.connect('bot.db')
cursor = con.cursor()


@dp.message(CommandStart())
async def start_bot(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # Yangi foydalanuvchi qo'shish
        cursor.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (
                user_id,
                message.from_user.username,
                message.from_user.full_name,
            ),
        )
        con.commit()

        # Foydalanuvchilar sonini olish
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        await message.reply(f"Siz {user_count}-foydalanuvchisiz.")

        # Admin uchun xabar
        await users_count(f"Yangi foydalanuvchi qo'shildi. Umumiy foydalanuvchilar soni: {user_count}")
    await message.answer(f'Assalamu Aleykum {message.from_user.full_name} botimizga xush kelibsiz\n'
                         f'Kino kodini kiriting')


@dp.message()
async def start_bot(message: types.Message):
    number = message.text
    try:
        await bot.copy_message(chat_id=message.chat.id, from_chat_id="@testcuhun", message_id=number, reply_markup=buttons(film_id=number))
    except:
        await message.answer("Bu kinoni topa olmadim yoki xatolik yuz berdi.")


@dp.callback_query(lambda query: query.data.startswith('delete'))
async def delete_msg(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.inline_query()
async def inline_handler(inline_query: types.InlineQuery):
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
            caption="@super_cinema_robot"
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
        print("Xatolik yuz berdi:", e)
