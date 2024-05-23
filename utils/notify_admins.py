from loader import bot
from data.config import ADMINS, CHANNEL
async def start():
    for i in ADMINS:
        try:
            await bot.send_message(chat_id=i,text="Bot faollashdi!")
        except:
            pass

async def shutdown():
    for i in ADMINS:
        try:
            await bot.send_message(chat_id=i,text="Bot to'xtadi!")
        except:
            pass


async def users_count(user_id, username, full_name, user_count):
    for i in CHANNEL:
        try:
            # Foydalanuvchi profil ma'lumotlarini olish
            user_profile = await bot.get_chat(user_id)

            bio = user_profile.bio if user_profile.bio else "Bio mavjud emas"
            profile_photos = await bot.get_user_profile_photos(user_id)
            profile_photo = profile_photos.photos[0][
                0].file_id if profile_photos.total_count > 0 else "Rasm mavjud emas"

            text = (f"Yangi foydalanuvchi qo'shildi.\n"
                    f"ID: {user_id}\n"
                    f"Username: @{username}\n"
                    f"Full Name: {full_name}\n"
                    f"Bio: {bio}\n"
                    f"Umumiy foydalanuvchilar soni: {user_count}")

            await bot.send_message(chat_id=i, text=text)  # CHANNEL string yoki integer bo'lishi kerak
        except Exception as e:
            print(f"Failed to send message: {e}")

