from aiogram import Bot,Dispatcher
from data.config import BOT_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
bot=Bot(token=BOT_TOKEN)
dp=Dispatcher(storage=MemoryStorage())
import sqlite3


con = sqlite3.connect("bot.db")
cursor = con.cursor()
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT
    )
    '''
)
con.commit()