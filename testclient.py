from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import os

# Замените эти значения на свои
API_ID = 24476076  # Ваш API ID
API_HASH = 'ee71cff9806c0c865b24ebdc9168fa68'  # Ваш API Hash
SESSION_FILE = 'session.session'  # Имя файла для хранения сессии

async def login_and_save_session(phone_number):
    """Авторизация в Telegram и сохранение сессии."""
    if not os.path.exists("sessions"):
        os.makedirs("sessions")
    session_file = f"sessions/{phone_number.replace('+', '')}.session"
    client = TelegramClient(session_file, API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"🔑 Отправлен код на номер {phone_number}...")
            await client.send_code_request(phone_number)
            
            code = input("Введите код из SMS или Telegram: ")
            await client.sign_in(phone_number, code)
            print("✅ Успешная авторизация!")
        if os.path.exists(session_file):
            print(f"📁 Сессия сохранена в: {session_file}")
        else:
            print("⚠️ Файл сессии не создан!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()


phone = input("Введите номер телефона (в формате +79991234567): ")
asyncio.run(login_and_save_session(phone))