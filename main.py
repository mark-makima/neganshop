import telebot
from telebot import types
import time 
import random
import logging
import json
import os
import threading
from pyCryptoPayAPI import pyCryptoPayAPI
import math
from pyrogram import Client
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from threading import Thread
import sqlite3
from telethon.errors import SessionPasswordNeededError
import re
from telethon.sessions import StringSession, SQLiteSession
from typing import Dict, Any
import requests









#------data-----------
TOKEN = '8387349171:AAH6SSWWEGqB6MBVYuJv9X_ndrA4oZrciIU'
TESTBOTTOKEN = '8359013435:AAGarvn9AmWfRlfGD1PcJtoVnpjBZEOtamI'
PAYMASTERKEY = '1744374395:TEST:0933cf0533093760f40a'
CRYPTOPAYTOKEN = '440288:AAu4JoPgW6aRAGoEbo3wFQlpZ3XZfhYSZcl'
TESTTOKEN = '45260:AAEb9GvuXnb9OFkJzWr6VejcQav1g9zQseB'
CARD = 2200701347647254
CHANNEL_ID = '@neganworks'
ADMINID = [768223541, 7220303850]
user_data = {}
current_message = {}
proxy = ('HTTP', '191.96.125.154', 8991, True, 'user314167', '3teq8a')
sort_states = {}
user_states = {}

crypto = pyCryptoPayAPI(api_token=CRYPTOPAYTOKEN, test_net=False)
bot = telebot.TeleBot(token=TOKEN)

# Введите свои данные
API_ID = 24476076  # Замените на ваш API ID
API_HASH = 'ee71cff9806c0c865b24ebdc9168fa68'  # Замените на ваш API Hash





# class TelegramFileSender:
#     def __init__(self):
#         self.channel_id = '-1002323342468'  # Например: '-1001234567890'
#         self.interval = 50  # Интервал в секундах (60 = 1 минута)
#         self.running = False
#         self.thread = None

#     def send_json_files(self):
#         while self.running:
#             try:
#                 # Получаем список JSON-файлов в указанной директории
                
#                 time.sleep(self.interval)

#                 try:
#                     with open('/data/users.json', 'rb') as file:
#                         bot.send_document(
#                             chat_id=self.channel_id,
#                             document=file,
#                             caption=f"Файл: пользователи"
#                         )
#                     print(f"Отправлен файл: пользователи")
#                 except Exception as e:
#                     print(f"Ошибка при отправке пользователи: {e}")

#                 try:
#                     with open('/data/lots.json', 'rb') as file:
#                         bot.send_document(
#                             chat_id=self.channel_id,
#                             document=file,
#                             caption=f"Файл: лоты"
#                         )
#                     print(f"Отправлен файл: лоты")
#                 except Exception as e:
#                     print(f"Ошибка при отправке лоты: {e}")
#                 try:
#                     with open('/data/cards.json', 'rb') as file:
#                         bot.send_document(
#                             chat_id=self.channel_id,
#                             document=file,
#                             caption=f"Файл: пополнения"
#                         )
#                     print(f"Отправлен файл: пополнения")
#                 except Exception as e:
#                     print(f"Ошибка при отправке пополнения: {e}")

#             except Exception as e:
#                 print(f"Общая ошибка: {e}")

#             time.sleep(self.interval)

#     def start(self):
#         if not self.running:
#             self.running = True
#             self.thread = threading.Thread(target=self.send_json_files)
#             self.thread.daemon = True  # Демон-поток (завершится с основной программой)
#             self.thread.start()
#             print("Сервис отправки файлов запущен")

#     def stop(self):
#         self.running = False
#         if self.thread:
#             self.thread.join()
#         print("Сервис отправки файлов остановлен")


# TelegramFileSender().start()

    

class JsonDataCleaner:
    def __init__(self, file_path: str, data_to_remove: Dict[str, Any]):
        """
        :param file_path: Путь к JSON файлу
        :param data_to_remove: Данные для удаления (ключи и значения)
        """
        self.file_path = file_path
        self.data_to_remove = data_to_remove
        self.timer = None

    def start_cleanup_timer(self, delay_minutes: int = 5):
        """Запускает таймер для очистки через указанное количество минут"""
        delay_seconds = delay_minutes * 60
        self.timer = threading.Timer(delay_seconds, self.cleanup_data)
        self.timer.start()
        print(f"Таймер очистки установлен на {delay_minutes} минут")

    def cleanup_data(self):
        """Удаляет указанные данные из JSON файла"""
        try:
            # Проверяем существование файла
            if not os.path.exists(self.file_path):
                print(f"Файл {self.file_path} не найден")
                return

            # Читаем данные из файла
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Удаляем указанные данные
            original_size = len(json.dumps(data))
            for key in self.data_to_remove:
                if key in data:
                    del data[key]

            # Записываем обратно только если данные изменились
            if len(json.dumps(data)) != original_size:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print("Данные успешно удалены")
            else:
                print("Данные для удаления не найдены")

        except json.JSONDecodeError:
            print("Ошибка: Файл не является валидным JSON")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
        finally:
            self.timer = None

    def cancel_cleanup(self):
        """Отменяет запланированную очистку"""
        if self.timer:
            self.timer.cancel()
            print("Таймер очистки отменен")
            self.timer = None

class TelegramAuth:
    def __init__(self):
        self.clients = {}
        self.loop = asyncio.new_event_loop()  # Создаем новый event loop
        os.makedirs("/data/sessions", exist_ok=True)

    def clean_phone_number(self, phone):
        """Очищает номер телефона от всех нецифровых символов"""
        return re.sub(r'[^0-9]', '', phone)

    async def _create_client(self, phone):
        """Создает клиента Telethon для номера"""
        session = StringSession()
        client = TelegramClient(
            session,
            API_ID,
            API_HASH,
            device_model="iPhone 14 Pro",
            system_version="19.0",
            app_version="8.4",
            lang_code="en",
            system_lang_code="en-US",
            proxy=proxy
        )
        self.clients[phone] = client
        return client

    async def _send_code(self, phone, chat_id):
        """Отправка кода подтверждения"""
        try:
            # Очищаем номер телефона перед использованием
            clean_phone = self.clean_phone_number(phone)
            client = await self._create_client(clean_phone)
            await client.connect()
            
            # Добавляем задержку перед запросом кода
            await asyncio.sleep(2)
            
            code_request = await client.send_code_request(clean_phone)
            user_states[chat_id] = {
                'phone': clean_phone,  # Сохраняем очищенный номер
                'code_hash': code_request.phone_code_hash,
                'waiting_code': True,
                'waiting_password': False
            }
            bot.send_message(chat_id, "🔑 Код подтверждения отправлен. Введите код из SMS:")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")
            if 'client' in locals():
                await asyncio.sleep(2)
                await client.disconnect()
    
    def start_auth(self, phone, chat_id):
        """Синхронная обертка для асинхронного метода _send_code"""
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._send_code(phone, chat_id))
        except Exception as e:
            print(f"Ошибка в start_auth: {e}")
            # Можно добавить обработку ошибки, например, отправить сообщение пользователю
            bot.send_message(chat_id, f"❌ Ошибка при отправке кода: {str(e)}")

    async def _confirm_code(self, chat_id, code):
        """Асинхронный метод подтверждения кода"""
        if chat_id not in user_states:
            return False

        data = user_states[chat_id]
        client = self.clients.get(data['phone'])
        
        if not client:
            return False

        try:
            await client.sign_in(
                phone=data['phone'],
                code=code,
                phone_code_hash=data['code_hash']
            )
            await asyncio.sleep(2)
            return await self._save_session_and_cleanup(client, data['phone'], chat_id)
        except SessionPasswordNeededError:
            user_states[chat_id]['waiting_password'] = True
            user_states[chat_id]['waiting_code'] = False
            bot.send_message(chat_id, "🔐 Требуется двухфакторная аутентификация. Введите пароль:")
            return False
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return False

    def confirm_code(self, chat_id, code):
        """Синхронная обёртка для _confirm_code"""
        asyncio.set_event_loop(self.loop)
        try:
            return self.loop.run_until_complete(self._confirm_code(chat_id, code))
        except Exception as e:
            print(f"Ошибка в confirm_code: {e}")
            return False
        
    def confirm_password(self, chat_id, password):
        asyncio.set_event_loop(self.loop)
        return self.loop.run_until_complete(self.confirm_password(chat_id, password))

    async def _save_session_and_cleanup(self, client, phone, chat_id):
        """Сохраняет сессию и выполняет очистку"""
        try:
            clean_phone = self.clean_phone_number(phone)
            session_file = f"/data/sessions/{clean_phone}.session"
            
            # Получаем строку сессии
            session_string = client.session.save()
            
            # Проверяем, что строка сессии не пустая
            if not session_string:
                raise ValueError("Empty session string")
            
            # Сохраняем в файл
            with open(session_file, 'w') as f:
                f.write(session_string)
                
            return True
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")
            return False
        finally:
            await client.disconnect()
            self.clients.pop(phone, None)
            user_states.pop(chat_id, None)

async def wait_for_verification_code(phone_number, timeout=300):
    """
    Ожидает код подтверждения от Telegram
    """
    # Очищаем номер телефона перед использованием
    clean_phone = re.sub(r'[^0-9]', '', phone_number)
    session_path = f"/data/sessions/{clean_phone}.session"
    
    await asyncio.sleep(2)
    if not os.path.exists(session_path):
        print(f"Файл сессии не найден: {session_path}")
        return None

    client = None
    try:
        with open(session_path, 'r') as f:
            content = f.read().strip()
        
        session = StringSession(content) if content.startswith('1') and len(content) > 100 else SQLiteSession(session_path)
        
        client = TelegramClient(
            session,
            api_id=API_ID,
            api_hash=API_HASH,
            proxy=proxy
        )
        await client.connect()
        
        if not await client.is_user_authorized():
            with open('/data/lots.json', 'r', encoding='utf8') as f:
                data = json.load(f)
            bot.send_message(chat_id=data[phone_number]['buyer'], 
                            text='Сессия не авторизована\nобратитесь в поддержку', 
                            parse_mode='Markdown')

        code_received = asyncio.Event()
        verification_code = None

        @client.on(events.NewMessage(incoming=True))
        async def handler(event):
            nonlocal verification_code
            text = event.message.text
            code = extract_verification_code(text, phone_number)
            if code:
                verification_code = code
                code_received.set()

        try:
            await asyncio.wait_for(code_received.wait(), timeout=timeout)
            return verification_code
        except asyncio.TimeoutError:
            with open('/data/lots.json', 'r', encoding='utf8') as f:
                data = json.load(f)
            bot.send_message(chat_id=data[phone_number]['buyer'], 
                            text='Время ожидания истекло, код не получен', 
                            parse_mode='Markdown')
            return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        if client and client.is_connected():
            await client.disconnect()
            print("Сессия закрыта")

def extract_verification_code(text, phone_number):
    """Извлекает 5-значный код подтверждения из текста"""
    if not text:
        return None
    
    # Точные паттерны для кодов Telegram
    patterns = [
        r'\b\d{5}\b',                     # Изолированные 5 цифр
        r'код[: ]*(\d{5})',               # Код: 12345
        r'code[: ]*(\d{5})',              # Code: 12345
        r'verify[: ]*(\d{5})',            # Verify: 12345
        r'подтверждени[:ея ]*(\d{5})'     # Подтверждение: 12345
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            code = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if code.isdigit() and len(code) == 5:
                with open('/data/lots.json', 'r', encoding='utf8')as f:
                    data = json.load(f)
                bot.send_message(chat_id=data[phone_number]['buyer'], text=f'Ваш код: `{code}`', parse_mode='Markdown')
                os.remove(f'/data/sessions/{phone_number}.session')
                bot.send_message(chat_id=data[phone_number]['buyer'], text=f'Сессия аккаунта удалена, вы сможете удалить ее вручную через 24 часа\n*Не забудьте подтвердить получение!*', parse_mode='Markdown')
                return code
    return None



def get_last_code_sync(phone_number):
    """Синхронная обертка"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(wait_for_verification_code(phone_number))
    except Exception as e:
        return verify_code.update({phone_number: f'Ошибка выполнения: {str(e)}'})
    finally:
        loop.close()

# Инициализация
tg_auth = TelegramAuth()
verify_code = {}



def paid(id, filename='paid.txt'):
    if checkinvoice(id, filename):
        return True 
    with open(filename, 'a') as file:
        file.write(f"{id}\n")
    return False

def checkinvoice(id, filename='paid.txt'):
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip() == str(id):
                    return True 
    except FileNotFoundError:
        return False
    return False  

def load_users():
    try:
        with open('/data/users.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        print('oshibka')
        data = {}
    return data

def create_invoice(m):
    try:
        amount = float(m.text)
        invoice = crypto.create_invoice(asset='USDT', amount=amount, description='💳 Пополнение баланса Negan физшоп', hidden_message='Баланс был пополнен.')
        print(invoice['status'])
        mrk = types.InlineKeyboardMarkup(row_width=1)
        but1 = types.InlineKeyboardButton(text='✔ Оплатить счет', url=invoice['pay_url'])
        but2 = types.InlineKeyboardButton(text='⚡ Я оплатил', callback_data=f'оплатил{invoice["invoice_id"]}')
        but5  = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
        mrk.add(but5)
        mrk.add(but1, but2)
        mes = bot.send_message(chat_id=m.from_user.id, text=f'Счет на сумму *{amount}*$ создан, _кнопка для оплаты счет ниже_', parse_mode='Markdown', reply_markup=mrk)
        current_message.update({str(call.from_user.id): mes.message_id})
    except Exception as e:
        print(e)
        bot.send_message(chat_id=m.from_user.id, text='*Некорректная сумма*!', parse_mode='Markdown')

def update_balance(user_id, amount_to_add, filename='/data/users.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if user_id in data:
            current_balance = data[user_id]['balance']
            new_balance = current_balance + amount_to_add
            data[user_id]['balance'] = new_balance
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return new_balance
        else:
            print(f"Пользователь с ID {user_id} не найден.")
            return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

def deupdate_balance(user_id, amount_to_min, filename='/data/users.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if user_id in data:
            current_balance = data[user_id]['balance']
            new_balance = current_balance - amount_to_min
            data[user_id]['balance'] = new_balance
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return new_balance
        else:
            print(f"Пользователь с ID {user_id} не найден.")
            return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None



def adminacc(m):
    if m.content_type == 'photo':
        mrk = types.InlineKeyboardMarkup(row_width=1)
        but1 = types.InlineKeyboardButton(text='✅ Пополнить баланс', callback_data=f'✅ Пополнить баланс{m.from_user.id}')
        but2 = types.InlineKeyboardButton(text='❌ Чек не корректный', callback_data=f'❌ Чек не корректный{m.from_user.id}')
        mrk.row(but1, but2)
        for id in ADMINID:
            bot.forward_message(chat_id=id, from_chat_id=m.from_user.id, message_id=m.message_id)
            bot.send_message(chat_id=id, text=f'*Чек от пользователя {m.from_user.id} ({m.from_user.username})*', parse_mode='Markdown', reply_markup=mrk)
        bot.send_message(chat_id=m.from_user.id, text=f'*Чек отправлен модератору, дождитесь проверки чека*', parse_mode='Markdown')
    else:
        bot.send_message(chat_id=m.from_user.id, text=f'*Чек можно отправить только ввиде фотографии!*', parse_mode='Markdown')

def next_step_card(m):
    try:
        with open('/data/cards.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    try:
        if not str(m.from_user.id) in data:
            amount = float(m.text)
            with open('/data/cards.json', 'w', encoding='utf8')as f:
                data[str(m.from_user.id)] = {
                    'amount': amount
                }
                json.dump(data, f, ensure_ascii=False, indent=4)
            mrk = types.InlineKeyboardMarkup(row_width=1)
            but5  = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
            mrk.add(but5)
            x = bot.send_message(chat_id=m.from_user.id, text=f'*Пополнение баланса {m.from_user.id}*\nсумма: `{amount}`\nКарта для оплаты: `{CARD}`\n\nУ вас есть 5 минут на оплату\n\n*После успешной оплаты пришлите чек в чат с ботом*', parse_mode='Markdown', reply_markup=mrk)
            current_message.update({str(m.from_user.id): x.message_id})
            clean = JsonDataCleaner(file_path='/data/cards.json', data_to_remove={str(m.from_user.id): None, 'amount': None})
            clean.start_cleanup_timer(delay_minutes=5)
            bot.register_next_step_handler(x, adminacc)
        else:
            bot.send_message(chat_id=m.from_user.id, text=f'*У вас уже есть заявка на пополнение баланса!*', parse_mode='Markdown')
    except Exception as e:
        print(e)
        bot.send_message(chat_id=m.from_user.id, text='*Некорректная сумма*!', parse_mode='Markdown')

def remove_dict_from_json(key_to_remove, file_path='/data/cards.json'):
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    if key_to_remove in data:
        del data[key_to_remove]
        print(f"Словарь с ключом '{key_to_remove}' был удален.")
    else:
        print(f"Словарь с ключом '{key_to_remove}' не найден.")
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def support_next_step(m):
    uid = random.randint(100, 99999)
    try:
        with open('/data/support.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
        print('y')
    print('z')
    
    if not str(uid) in data:
        print('x')
        data[str(uid)] = {
            'id': str(m.from_user.id),
            'text': str(m.text)
        }
        with open('/data/support.json', 'w', encoding='utf8')as x:
            json.dump(data, x, ensure_ascii=False, indent=4)
    else:
        support_next_step
        return None
    for id in ADMINID:
        try:
            bot.send_message(chat_id=id, text=f'*Обращение №{uid} от {m.from_user.username}*:\n{m.text}', parse_mode='Markdown')
        except: pass
    mrk = types.InlineKeyboardMarkup(row_width=1)
    but4 = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
    mrk.add(but4)
    mes = bot.send_message(chat_id=m.from_user.id, text=f'Ваше обращение было отправленно. Номер обращения: *№{uid}*', parse_mode='Markdown', reply_markup=mrk)
    current_message.update({str(m.from_user.id): mes.message_id})

def codesend(m):
    with open('/data/lots.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    mrk = types.InlineKeyboardMarkup(row_width=1)
    mrk.add(types.InlineKeyboardButton(text='🔄 Повторно запросить код', callback_data=f'📲 Запросить код{numbertosend}'))
    bot.send_message(chat_id=data[numbertosend]['buyer'], text=f'Ваш код: `{m.text}`\nНе забудьте подтвердить оплату!', parse_mode='Markdown', reply_markup=mrk)

@bot.message_handler(['start'])
def start(m: types.Message):
    chat_member = bot.get_chat_member(chat_id='@stillnegan', user_id=m.from_user.id)
    if chat_member.status in ['member', 'administrator', 'creator']:
        pass
    else:
        mrkx = types.InlineKeyboardMarkup(row_width=2)
        mrkx.add(types.InlineKeyboardButton(text='Подписатся ➕', url='https://t.me/stillnegan'))
        bot.send_message(chat_id=m.from_user.id, text=f'*Для работы с ботом подпишитесь на наш канал*\n_туда будут выкладыватся все обновления бота и важная инфорация полезная для вас_\n', parse_mode='Markdown', reply_markup=mrkx)
        return None
    mrk = types.InlineKeyboardMarkup(row_width=1)
    but1 = types.InlineKeyboardButton(text='👤 Профиль', callback_data='👤 Профиль')
    but2 = types.InlineKeyboardButton(text='📦 Каталог товаров', callback_data='📦 Каталог товаров')
    but3 = types.InlineKeyboardButton(text='➕ Пополнить баланс', callback_data='➕ Пополнить баланс')
    but4 = types.InlineKeyboardButton(text='🛠 Поддержка', callback_data='🛠 Поддержка')
    but5 = types.InlineKeyboardButton(text='🌟 Отзывы бота', callback_data='🌟 Отзывы бота')
    mrk.row(but1, but3)
    mrk.add(but4, but2)
    mrk.add(but5)
    if m.from_user.id in ADMINID:
        buta = types.InlineKeyboardButton(text='⚙ Админ-панель', callback_data='⚙ Админ-панель')
        mrk.add(buta)
    data = load_users()
    if not str(m.from_user.id) in data:
        with open('/data/users.json', 'w', encoding='utf8')as f:
            data[str(m.from_user.id)] = {
                'username': m.from_user.username,
                'balance': 0,
                'purchases': ''
            }
            json.dump(data, f, ensure_ascii=False, indent=4)
    photo = open('startphoto.jpg', 'rb')
    bot.send_photo(chat_id=m.from_user.id, photo=photo, caption=f'👋 *Добро пожаловать, {m.from_user.username}*\n------------------------------------\n💳 баланс: `{data[str(m.from_user.id)]['balance']}`\n🌟 ваши покупки: `Доступно в разделе "профиль"`\n------------------------------------\n*Магазин с качественно отобранными и обработанными аккаунтами по самым лучшим ценам*\n\nВыберите интересующий раздел', parse_mode='Markdown', reply_markup=mrk)

@bot.callback_query_handler(func=lambda call: call.data=='👤 Профиль')
def account(call: types.CallbackQuery):
   
    mrk = types.InlineKeyboardMarkup(row_width=1)
    but2 = types.InlineKeyboardButton(text='📦 Каталог товаров', callback_data='📦 Каталог товаров')
    but3 = types.InlineKeyboardButton(text='➕ Пополнить баланс', callback_data='➕ Пополнить баланс')
    but4 = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
    mrk.row(but2, but3)
    mrk.add(but4)
    bot.answer_callback_query(call.id, f"👤 Профиль")
    bot.send_message(chat_id=call.from_user.id, text='🗂')
    with open('/data/users.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    purchases = data[str(call.from_user.id)]['purchases']
    datapurchases = ''
    for i in purchases:
        if i == ' ':
            x = i.replace(' ', '\n')
            datapurchases+=x
        else:
            datapurchases+=i
    mes = bot.send_message(chat_id=call.from_user.id, text=f'*👤 Профиль {call.from_user.username}*\n\nID: {call.from_user.id}\nБаланс: {data[str(call.from_user.id)]['balance']}₽\n\n*Ваши покупки:*\n{datapurchases}', parse_mode="Markdown", reply_markup=mrk)
    current_message.update({str(call.from_user.id): mes.message_id})

@bot.callback_query_handler(func=lambda call: call.data=='🖥 Главное меню')
def mainmenu(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.from_user.id, message_id=current_message[str(call.from_user.id)])
    start(m=call)

@bot.callback_query_handler(func=lambda call: call.data=='🌟 Отзывы бота')
def review(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, f"🌟 Отзывы бота")
    mrk = types.InlineKeyboardMarkup(row_width=2)
    but4 = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
    mrk.add(but4)
    mrk.add(types.InlineKeyboardButton(text='⚡ Перейти в канал', url='https://t.me/neganworks'))
    mes = bot.send_message(chat_id=call.from_user.id, text=f'🌟 *Отзывы бота от наших клиентов вы можете увидеть в нашем канале*, нажмите кнопку ниже что бы перейти в канал', parse_mode='Markdown', reply_markup=mrk)
    current_message.update({str(call.from_user.id): mes.message_id})

items_per_page = 4
current_page = {}
user_catalog_message_ids = {}


def generate_keyboard(keys_on_page, total_pages, chat_id):
    try:
        with open('/data/lots.json', 'r', encoding='utf-8') as f:
            lots_data = json.load(f)
    except FileNotFoundError:
        print("Ошибка: файл data/lots.json не найден. Убедитесь, что он существует и доступен.")
        lots_data = {}
    except json.JSONDecodeError:
        print("Ошибка: файл data/lots.json содержит неверный JSON формат.")
        lots_data = {}
    
    keyboard = types.InlineKeyboardMarkup()
    
    for key in keys_on_page:
        if key in lots_data and all(k in lots_data[key] for k in ['country', 'otlega', 'price']) and lots_data[key]['status'] == 'Активен':
            keyboard.add(types.InlineKeyboardButton(
                text=f"{lots_data[key]['country']} || {lots_data[key]['otlega']} || {lots_data[key]['price']}₽", 
                callback_data=f'лот№{key}'))
        else:
            print(f"Предупреждение: Лот {key} не содержит всех необходимых данных (country, otlega, price).")
    
    # Добавляем кнопку сортировки
    sort_text = "🔢 Отсортировать"
    if sort_states.get(chat_id, 0) == 1:
        sort_text = "🔽 По убыванию"
    elif sort_states.get(chat_id, 0) == 2:
        sort_text = "🔼 По возрастанию"
    
    
    
    page_num_display = current_page.get(chat_id, 1)
    count = types.InlineKeyboardButton(text=f'{page_num_display}/{total_pages}', callback_data='no_action')
    
    if page_num_display > 1 and page_num_display < total_pages:
        keyboard.row(
            types.InlineKeyboardButton(text='◀️', callback_data='prev_page'), 
            count, 
            types.InlineKeyboardButton(text='▶️', callback_data='next_page')
        )
    elif page_num_display > 1:
        keyboard.row(
            types.InlineKeyboardButton(text='◀️', callback_data='prev_page'), 
            count
        )
    elif page_num_display < total_pages:
        keyboard.row(
            count, 
            types.InlineKeyboardButton(text='▶️', callback_data='next_page')
        )
    keyboard.row(types.InlineKeyboardButton(text=sort_text, callback_data='sort_lots'))
    but5 = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
    keyboard.add(but5)
    
    return keyboard

def show_page(chat_id, total_pages):
    try:
        with open('/data/lots.json', 'r', encoding='utf-8') as f:
            lots_data = json.load(f)
    except FileNotFoundError:
        print("Ошибка: файл data/lots.json не найден. Убедитесь, что он существует и доступен.")
        lots_data = {}
    except json.JSONDecodeError:
        print("Ошибка: файл data/lots.json содержит неверный JSON формат.")
        lots_data = {}
    
    # Получаем текущее состояние сортировки
    sort_state = sort_states.get(chat_id, 0)
    
    # Сортируем ключи лотов в зависимости от состояния сортировки
    all_lot_keys = list(lots_data.keys())
    if sort_state == 1:  # по убыванию цены
        all_lot_keys.sort(key=lambda k: float(lots_data[k]['price']), reverse=True)
    elif sort_state == 2:  # по возрастанию цены
        all_lot_keys.sort(key=lambda k: float(lots_data[k]['price']))
    
    page_number = current_page.get(chat_id, 1) 
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page    
    keys_on_page = all_lot_keys[start_index:end_index]
    
    keyboard = generate_keyboard(keys_on_page, total_pages, chat_id)
    caption_text = 'Приветствуем в *каталоге товаров*\nВыберите подходящий для вас номер' 
    
    if chat_id in user_catalog_message_ids:
        try:
            bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=user_catalog_message_ids[chat_id],
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Ошибка при редактировании сообщения каталога для чата {chat_id}: {e}")
            try:
                with open('ourlots.jpg', 'rb') as photo_file:
                    message = bot.send_photo(
                        chat_id=chat_id,
                        photo=photo_file,
                        caption=caption_text,
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )
                user_catalog_message_ids[chat_id] = message.message_id
                current_message.update({str(chat_id): user_catalog_message_ids[chat_id]})
            except FileNotFoundError:
                bot.send_message(chat_id, "Ошибка")
            except Exception as send_e:
                print(f"Ошибка при отправке нового сообщения каталога: {send_e}")
                bot.send_message(chat_id, "Произошла ошибка при отображении каталога.")  
    else:
        try:
            with open('ourlots.jpg', 'rb') as photo_file:
                message = bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption_text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            user_catalog_message_ids[chat_id] = message.message_id
            current_message.update({str(chat_id): user_catalog_message_ids[chat_id]})
        except FileNotFoundError:
            bot.send_message(chat_id, "Ошибка")
        except Exception as send_e:
            print(f"Ошибка при отправке нового сообщения каталога: {send_e}")
            bot.send_message(chat_id, "Произошла ошибка при отображении каталога.")

# Добавляем обработчик для кнопки сортировки
@bot.callback_query_handler(func=lambda call: call.data == 'sort_lots')
def handle_sort(call: types.CallbackQuery):
    chat_id = call.from_user.id
    
    # Получаем текущее состояние сортировки и меняем его
    current_sort = sort_states.get(chat_id, 0)
    if current_sort == 0 or current_sort == 2:
        new_sort = 1  # сортировка по убыванию
        bot.answer_callback_query(call.id, "Сортировка по убыванию цены")
    else:
        new_sort = 2  # сортировка по возрастанию
        bot.answer_callback_query(call.id, "Сортировка по возрастанию цены")
    
    sort_states[chat_id] = new_sort
    
    # Обновляем страницу
    try:
        with open('/data/lots.json', 'r', encoding='utf-8') as f:
            lots_data = json.load(f)
        total_items = len(lots_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Сбрасываем номер страницы на первую при сортировке
        current_page[chat_id] = 1
        
        show_page(chat_id, total_pages)
    except Exception as e:
        print(f"Ошибка при сортировке: {e}")
        bot.send_message(chat_id, "Произошла ошибка при сортировке каталога")

@bot.callback_query_handler(func=lambda call: call.data == '📦 Каталог товаров')
def catalogx(call: types.CallbackQuery):
    try:
        with open('/data/lots.json', 'r', encoding='utf-8') as f:
            lots_data = json.load(f)
    except FileNotFoundError:
        print("Ошибка: файл data/lots.json не найден. Убедитесь, что он существует и доступен.")
        lots_data = {}
    except json.JSONDecodeError:
        print("Ошибка: файл data/lots.json содержит неверный JSON формат.")
        lots_data = {}
    
    bot.answer_callback_query(call.id, "Открываю каталог товаров...")
    chat_id = call.from_user.id
    
    # Сбрасываем состояние сортировки при открытии каталога
    sort_states[chat_id] = 0
    
    try:
        total_items = len(lots_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        if total_pages == 0:
            bot.send_message(chat_id, "В данный момент нет доступных лотов.")
            return
        current_page[chat_id] = 1
        show_page(chat_id, total_pages)
    except Exception as e:
        print(f"Ошибка в catalogx: {e}")
        bot.send_message(chat_id, f"Произошла ошибка при открытии каталога")

@bot.callback_query_handler(func=lambda call: call.data in ['next_page', 'prev_page', 'no_action'])
def handle_navigation(call: types.CallbackQuery):
    try:
        with open('/data/lots.json', 'r', encoding='utf-8') as f:
            lots_data = json.load(f)
    except FileNotFoundError:
        print("Ошибка: файл data/lots.json не найден. Убедитесь, что он существует и доступен.")
        lots_data = {}
    except json.JSONDecodeError:
        print("Ошибка: файл data/lots.json содержит неверный JSON формат.")
        lots_data = {}
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    if chat_id not in current_page:
        bot.send_message(chat_id, "Состояние каталога утеряно. Пожалуйста, откройте каталог заново.")
        return

    total_items = len(lots_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    if total_pages == 0:
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=user_catalog_message_ids.get(chat_id),
            caption="В данный момент нет доступных лотов.",
            parse_mode='Markdown',
            reply_markup=None
        )
        return

    if call.data == 'next_page':
        if current_page[chat_id] < total_pages:
            current_page[chat_id] += 1
            show_page(chat_id, total_pages)
    elif call.data == 'prev_page':
        if current_page[chat_id] > 1:
            current_page[chat_id] -= 1
            show_page(chat_id, total_pages)
    

    
@bot.callback_query_handler(func=lambda call: call.data.startswith('лот№'))
def eachlot(call: types.CallbackQuery):
    number = call.data.replace('лот№', '')
    bot.answer_callback_query(call.id, f"лот№{number[-4:]}")
    password = ''
    numx = ''
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
            for i in data[number]['pass']:
                password+='-'
            for i in data[number]:
                numx+='-'
            if data[number]['status'] != 'Активен':
                bot.send_message(chat_id=call.from_user.id, text='*Лот уже куплен!*\nПрисмотритесь к другим вариантам :)', parse_mode='Markdown')
                return 'Куплен'
        mrk = types.InlineKeyboardMarkup(row_width=1)
        buy = types.InlineKeyboardButton(text='✅ Купить номер', callback_data=f'✅ Купить номер{number}')
        backtocatalog = types.InlineKeyboardButton(text='↩ Обратно в каталог', callback_data='backcatalog')
        mrk.row(buy, backtocatalog)
        bot.send_message(
        chat_id=call.from_user.id,
        text=(
            f'Лот *№{number[-4:]}*:\n'
            f'Номер: *{numx}* (скрыт)\n'
            f'Пароль: *{password}* (скрыт)\n'
            f'Отлега: *{data[number]["otlega"]}*\n'
            f'Тип выдачи: *{data[number]["type"]}*\n'
            f'Цена: *{data[number]["price"]}₽*\n\n'
            '💡 Скрытая информация будет доступна *после покупки* номера\n\n'
            '🔑 Лот с типом выдачи "Ручной" выдается вручную модератором\n\n'
            '🤖 Лот с типом выдачи "Автоматический" выдается системой, *оплата так же списывается автоматически*\n\n'
            '❗️ После входа в аккаунт вам нужно *подтвердить заказ в течение 5 минут*, иначе средства будут списаны автоматически'
        ),
        parse_mode='Markdown',
        reply_markup=mrk
        )   
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.from_user.id, text=f'*Произошла ошибка при получении данных лота!*\nПопробуйте еще раз либо выберите другой лот', parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('backcatalog'))
def backcatalog(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "↩")
    catalogx(call=call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('✅ Купить номер'))
def stepbuy(call: types.CallbackQuery):
    number = call.data.replace('✅ Купить номер', '')
    bot.answer_callback_query(call.id, f"✅ Купить номер")
    mrk = types.InlineKeyboardMarkup(row_width=1)
    mrk.add(types.InlineKeyboardButton(text='⚡ Я ознакомился, перейти к покупке', callback_data=f'покупка{number}'))
    with open('/data/lots.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    if data[number]['status'] == 'Активен':
        bot.send_message(
        chat_id=call.from_user.id,
        text='Перед оформлением заказа ознакомтесь с <a href="https://teletype.in/@negan_smith_shop/aHbYCA4LAsC">правилами</a> бота.',
        parse_mode='HTML', 
        reply_markup=mrk,
        disable_web_page_preview=True
            )
@bot.callback_query_handler(func=lambda call: call.data.startswith('покупка'))
def buynum(call: types.CallbackQuery):
    global numbertosend
    numbertosend = ''
    bot.answer_callback_query(call.id, f"покупка")
    number = call.data.replace('покупка', '')
    numbertosend+=number
    with open('/data/users.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    with open('/data/lots.json', 'r', encoding='utf8')as x:
        numbers = json.load(x)
    if data[str(call.from_user.id)]['balance'] >= float(numbers[number]['price']):
        if numbers[number]['status'] == 'Активен':
            deupdate_balance(user_id=str(call.from_user.id), amount_to_min=float(numbers[number]['price']))
            with open('/data/lots.json', 'w', encoding='utf8')as z:
                numbers[number]['status'] = "Куплен"
                numbers[number]['buyer'] = str(call.from_user.id)
                json.dump(numbers, z, ensure_ascii=False, indent=4)
            
            mrk = types.InlineKeyboardMarkup(row_width=1)
            but1 = types.InlineKeyboardButton(text='📲 Запросить код', callback_data=f'📲 Запросить код{number}')
            but2 = types.InlineKeyboardButton(text='🔓 Подтвердить получение', callback_data=f'🔓 Подтвердить получение{number}')
            mrk.row(but1, but2)
            bot.send_message(
            chat_id=call.from_user.id,
            text=(
                f'Лот *№{number[-4:]}*:\n'
                f'Номер: *{number}* \n'
                f'Пароль: *{numbers[number]['pass']}*\n'
                f'Отлега: *{numbers[number]["otlega"]}*\n'
                f'Тип выдачи: *{numbers[number]["type"]}*\n'
                f'Цена: *{numbers[number]["price"]}₽*\n\n'
                '❗️ После входа в аккаунт вам нужно *подтвердить заказ в течение 5 минут*, иначе средства будут списаны автоматически\n\n'
                f'_Код авторизации будет автоматически выслан вам в течение 5 минут_\nЕсли код не пришел *обратитесь в поддержку*'
            ),
            parse_mode='Markdown',
            reply_markup=mrk
            )  

            if numbers[number]["type"] == 'Ручной':
                for id in ADMINID:
                    bot.send_message(chat_id=id, 
                    text=(
                        f'*Новая покупка!*\n\n'
                        f'Покупатель: {call.from_user.username}\n'
                        f'Лот *№{number[-4:]}*:\n'
                        f'Номер: *{number}* \n'
                        f'Пароль: *{numbers[number]['pass']}*\n'
                        f'Отлега: *{numbers[number]["otlega"]}*\n'
                        f'Тип выдачи: *{numbers[number]["type"]}*\n'
                        f'Цена: *{numbers[number]["price"]}₽*\n\n'
                        '_Вы сможете отправить код после того как пользователь нажмет соответствующую кнопку_'
                    ),
                    parse_mode='Markdown',
                    )
            else:
                try:
                    for id in ADMINID:
                        bot.send_message(chat_id=id, 
                        text=(
                            f'*Новая покупка!*\n\n'
                            f'Покупатель: {call.from_user.username}\n'
                            f'Лот *№{number[-4:]}*:\n'
                            f'Номер: *{number}* \n'
                            f'Пароль: *{numbers[number]['pass']}*\n'
                            f'Отлега: *{numbers[number]["otlega"]}*\n'
                            f'Тип выдачи: *{numbers[number]["type"]}*\n'
                            f'Цена: *{numbers[number]["price"]}₽*\n\n'
                            '_Лот будет автоматически выдан пользователю_'
                        ),
                        parse_mode='Markdown',
                        )
                    get_last_code_sync(phone_number=number)        
                except Exception as e:
                    print(e)
                    pass
                              
        else:
            bot.send_message(chat_id=call.from_user.id, text='*Извините, лот уже купили\nПрисмотритесь к другим лотам*', parse_mode='Markdown')
    else:
        bot.send_message(chat_id=call.from_user.id, text='*У вас недостаточно средств!\nПополните баланс и возвращайтесь к лоту*', parse_mode='Markdown')

def sendotzyv(m):
    bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=m.chat.id, message_id=m.message_id)
    bot.send_message(chat_id=m.from_user.id, text='Благодарим вас за отзыв! Ждем вас снова :)')

@bot.callback_query_handler(func=lambda call: call.data.startswith('🌟 Оставить отзыв'))
def addotzyv(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "🌟 Оставить отзыв")
    x = bot.send_message(chat_id=call.from_user.id, text=f'*Пришлите свой отзыв по примеру ниже* ⬇\n`+rep @shopnegan_bot хорошие цены, быстро выдали номер`', parse_mode='Markdown')
    bot.register_next_step_handler(x, sendotzyv)

@bot.callback_query_handler(func=lambda call: call.data.startswith('🔓 Подтвердить получение'))
def acceptnumber(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "🔓 Подтвердить получение")
    number = call.data.replace('🔓 Подтвердить получение', '')
    with open('/data/lots.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    with open('/data/users.json', 'r', encoding='utf8')as x:
        users = json.load(x)
    with open('/data/users.json', 'w', encoding='utf8')as x:
        users[str(call.from_user.id)]['purchases'] += f'{number} '
        json.dump(users, x, ensure_ascii=False, indent=4)
    mrk = types.InlineKeyboardMarkup(row_width=1)
    mrk.add(types.InlineKeyboardButton(text='🌟 Оставить отзыв', callback_data='🌟 Оставить отзыв'))
    bot.send_message(chat_id=data[numbertosend]['buyer'], 
                    text=('*Благодарим за покупку* ❤\nВаш заказ:\n\n'
                        f'Лот *№{number[-4:]}*:\n'
                        f'Номер: *{number}* \n'
                        f'Пароль: *{data[number]['pass']}*\n'
                        f'Отлега: *{data[number]["otlega"]}*\n'
                        f'Тип выдачи: *{data[number]["type"]}*\n'
                        f'Цена: *{data[number]["price"]}₽*\n\n'
                        '*❗ Пожалуйста, оставьте свой отзыв по кнопке ниже*\n'
                        'Ждем вас снова!'
                    ), 
                    parse_mode='Markdown',
                    reply_markup=mrk)
    
    time.sleep(2)
    with open('/data/users.json', 'r', encoding='utf8')as x:
        users = json.load(x)
    del data[number]
    with open('/data/lots.json', 'w', encoding='utf8')as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    

@bot.callback_query_handler(func=lambda call: call.data.startswith('📲 Запросить код'))
def reqcode(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "📲 Запросить код")
    number = call.data.replace('📲 Запросить код', '')
    with open('/data/lots.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    if data[number]['type'] == 'Ручной':
        mrk = types.InlineKeyboardMarkup(row_width=1)
        but1 = types.InlineKeyboardButton(text='📲 Отправить код', callback_data=f'📲 Отправить код{number}')
        mrk.add(but1)
        bot.send_message(chat_id=call.from_user.id, text='*Ожидайте код от модератора*', parse_mode='Markdown')
        for id in ADMINID:
            bot.send_message(chat_id=id, text=f'Пользователь *{call.from_user.username}* запросил код на номер *{number}* ', parse_mode='Markdown', reply_markup=mrk)
    
        

@bot.callback_query_handler(func=lambda call: call.data.startswith('📲 Отправить код'))
def sendcode(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "📲 Отправить код")
    global numbertosend
    numbertosend = ''
    numbertosend+=call.data.replace('📲 Отправить код', '')
    x = bot.send_message(chat_id=call.from_user.id, text='Отправьте код:')
    bot.register_next_step_handler(x, codesend)
    
@bot.callback_query_handler(func=lambda call: call.data=='◀ Назад')
def back(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "◀ Назад")
    start(m=call)

@bot.callback_query_handler(func=lambda call: call.data=='⚙ Админ-панель')
def adminconsole(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "⚙ Админ-панель")
    if call.from_user.id in ADMINID:
        mrk = types.InlineKeyboardMarkup(row_width=1)
        but1 = types.InlineKeyboardButton(text='📞 Добавить лот', callback_data='📞 Добавить лот')
        but2 = types.InlineKeyboardButton(text='🤖 Заявки в поддержке', callback_data='🤖 Заявки в поддержке')
        but3 = types.InlineKeyboardButton(text='❌ Удалить лот', callback_data='❌ Удалить лот')
        but4 = types.InlineKeyboardButton(text='💳 Заявки на пополнение', callback_data='💳 Заявки на пополнение')
        but5  = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
        mrk.add(but1, but2, but3, but4)
        mrk.add(but5)
        mes = bot.send_message(chat_id=call.from_user.id, text=f'Добро пожаловать, *{call.from_user.username}*\nвыберите пунк управления', parse_mode='Markdown', reply_markup=mrk)
        current_message.update({str(call.from_user.id): mes.message_id})

@bot.callback_query_handler(func=lambda call: call.data=='💳 Заявки на пополнение')
def delcard(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "❌ Удалить лот")
    try:
        with open('/data/cards.json', 'r', encoding='utf8')as f:
            data = json.load(f)
            mrk = types.InlineKeyboardMarkup(row_width=1)
            for key in data:
                mrk.add(types.InlineKeyboardButton(text=f'{key} | {data[key]['amount']} ❌', callback_data=f'remove{key}'))
            but5  = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
            mrk.add(but5)
            bot.send_message(chat_id=call.from_user.id, text='*Заявки доступные для удаления*', parse_mode='Markdown', reply_markup=mrk)
    except:
        bot.send_message(chat_id=call.from_user.id, text='*Нет заявок для удаления!*', parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('remove'))
def remcard(call: types.CallbackQuery):
    lot = call.data.replace('remove', '')
    bot.answer_callback_query(call.id, "rem")
    with open('/data/cards.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    del data[lot]
    with open('/data/cards.json', 'w', encoding='utf8')as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    bot.send_message(chat_id=call.from_user.id, text=f'*Заявка №{lot} удалена*', parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data=='❌ Удалить лот')
def dellot(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "❌ Удалить лот")
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
            mrk = types.InlineKeyboardMarkup(row_width=1)
            for key in data:
                mrk.add(types.InlineKeyboardButton(text=f'{key} | {data[key]['status']} ❌', callback_data=f'del{key}'))
            but5  = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
            mrk.add(but5)
            mes = bot.send_message(chat_id=call.from_user.id, text='*Лоты доступные для удаления*', parse_mode='Markdown', reply_markup=mrk)
            current_message.update({str(call.from_user.id): mes.message_id})
    except:
        bot.send_message(chat_id=call.from_user.id, text='*Нет лотов для удаления!*', parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('del'))
def dellott(call: types.CallbackQuery):
    lot = call.data.replace('del', '')
    bot.answer_callback_query(call.id, "del")
    with open('/data/lots.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    del data[lot]
    with open('/data/lots.json', 'w', encoding='utf8')as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    bot.send_message(chat_id=call.from_user.id, text=f'*Лот №{lot} удален*', parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data=='🤖 Заявки в поддержке')
def supportmod(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "🤖 Заявки в поддержке")
    try:
        with open('/data/support.json', 'r', encoding='utf8')as f:
            data = json.load(f)
            mrk = types.InlineKeyboardMarkup(row_width=1)
            for key in data:
                mrk.add(types.InlineKeyboardButton(text=f'заявка №{key} от пользователя {data[key]['id']}', callback_data=f'заявка{key}'))
            bot.send_message(chat_id=call.from_user.id, text='🤖 Техническая поддержка', reply_markup=mrk)
    except FileNotFoundError:
        data = {}
        bot.send_message(chat_id=call.from_user.id, text='🤖 Техническая поддержка\n*Заявок нет*', parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('заявка'))
def supportansw(call: types.CallbackQuery):
    uid = call.data.replace('заявка', '')
    bot.answer_callback_query(call.id, f"Заявка №{uid}")
    with open('/data/support.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    mrk = types.InlineKeyboardMarkup(row_width=1)
    but1 = types.InlineKeyboardButton(text='✍ Ответить', callback_data=f'✍ Ответить{uid}')
    but2 = types.InlineKeyboardButton(text='❌ Удалить', callback_data=f'❌ Удалить{uid}')
    mrk.row(but1, but2)
    bot.send_message(chat_id=call.from_user.id, text=f'Заявка *№{uid}* от пользователя {data[uid]['id']}:\n_{data[uid]['text']}_', parse_mode='Markdown', reply_markup=mrk) 

@bot.callback_query_handler(func=lambda call: call.data.startswith('❌ Удалить'))
def supportansw(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "❌ Удалить")
    uid = call.data.replace('❌ Удалить', '')
    with open('/data/support.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    del data[uid]
    with open('/data/support.json', 'w', encoding='utf8')as x:
        json.dump(data, x, ensure_ascii=False, indent=4)
    bot.send_message(chat_id=call.from_user.id, text=f'заявка №{uid} удалена')



def answersupport(m):
    with open('/data/support.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    user = data[currzayavka]['id']
    bot.send_message(chat_id=user, text=f'Сообщение от модератора (заявка №{currzayavka}):\n{m.text}')
    bot.send_message(chat_id=m.from_user.id, text=f'Отправленно')

@bot.callback_query_handler(func=lambda call: call.data.startswith('✍ Ответить'))
def supportansw(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "✍ Ответить")
    uid = call.data.replace('✍ Ответить', '')
    x = bot.send_message(chat_id=call.from_user.id, text=f'пришлите текст для отправки №{uid}')
    global currzayavka
    currzayavka = ''
    currzayavka+=uid
    bot.register_next_step_handler(x, answersupport)

@bot.callback_query_handler(func=lambda call: call.data=='📞 Добавить лот')
def addlot(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "📞 Добавить лот")
    lots = ''
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
        for key in data:
            lots+=f'{key}\nСтрана: {data[key]['country']}\nотлега: {data[key]['otlega']}\nпароль: {data[key]['pass']}\nспособ выдачи: {data[key]['type']}\nстатус: {data[key]['status']}\n\n'
    except FileNotFoundError:
        lots+='*Нет номеров в каталоге!*'
        data = {}
    mrk = types.InlineKeyboardMarkup(row_width=1)
    but1 = types.InlineKeyboardButton(text='➕ Добавить номер', callback_data='➕ Добавить номер')
    mrk.add(but1)
    bot.send_message(chat_id=call.from_user.id, text=f'Текущие номера в лотах:\n{lots}', parse_mode='Markdown', reply_markup=mrk)



def numbernextstep(m):
    user_states[m.from_user.id] = {'step': 'waiting_phone'}
    global num
    num = ''
    num += m.text
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    with open('/data/lots.json', 'w', encoding='utf8')as x:
        data[str(num)] = {
            'country': 0,
            'otlega': 0,
            'pass': 0,
            'type': 0,
            'price': 0,
            'status': 0
        }
        json.dump(data, x, ensure_ascii=False, indent=4)
    x = bot.send_message(chat_id=m.from_user.id, text='Окей, теперь пришлите страну номера')
    bot.register_next_step_handler(x, countrynextstep)

def countrynextstep(m):
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    with open('/data/lots.json', 'w', encoding='utf8')as x:
        data[str(num)] = {
            'country': m.text,
            'otlega': 0,
            'pass': 0,
            'type': 0,
            'price': 0,
            'status': 0
        }
        json.dump(data, x, ensure_ascii=False, indent=4)
    x = bot.send_message(chat_id=m.from_user.id, text='Хорошо, теперь пришлите отлегу номера')
    bot.register_next_step_handler(x, otleganextstep)

def otleganextstep(m):
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    with open('/data/lots.json', 'w', encoding='utf8')as x:
        data[str(num)] = {
            'country': data[str(num)]['country'],
            'otlega': m.text,
            'pass': 0,
            'type': 0,
            'price': 0,
            'status': 0
        }
        json.dump(data, x, ensure_ascii=False, indent=4)
    x = bot.send_message(chat_id=m.from_user.id, text='Отлично, теперь пришлите пароль от аккаунта')
    bot.register_next_step_handler(x, passnextstep)

def passnextstep(m):
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    with open('/data/lots.json', 'w', encoding='utf8')as x:
        data[str(num)] = {
            'country': data[str(num)]['country'],
            'otlega': data[str(num)]['otlega'],
            'pass': m.text,
            'type': 0,
            'price': 0,
            'status': 0,
            'buyer': ''
        }
        json.dump(data, x, ensure_ascii=False, indent=4)
    x = bot.send_message(chat_id=m.from_user.id, text='Отлично, теперь установите цену (в рублях)')
    bot.register_next_step_handler(x, pricenextstep)

def pricenextstep(m):
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    with open('/data/lots.json', 'w', encoding='utf8')as x:
        data[str(num)] = {
            'country': data[str(num)]['country'],
            'otlega': data[str(num)]['otlega'],
            'pass': data[str(num)]['pass'],
            'type': 0,
            'price': int(m.text),
            'status': 0
        }
        json.dump(data, x, ensure_ascii=False, indent=4)
    mrk = types.InlineKeyboardMarkup(row_width=1)
    mrk.add(types.InlineKeyboardButton(text='Автоматический', callback_data=f'Автоматический{num}'), types.InlineKeyboardButton(text='Ручной', callback_data=f'Ручной{num}'))
    x = bot.send_message(chat_id=m.from_user.id, text='Отлично, теперь выберите тип выдачи', reply_markup=mrk)

    
@bot.callback_query_handler(func=lambda call: call.data.startswith('Автоматический'))
def auto(call: types.CallbackQuery):
    num = call.data.replace('Автоматический', '')
    
    # Инициализация tg_auth при первом вызове
    if not hasattr(bot, 'tg_auth'):
        bot.tg_auth = TelegramAuth()
        print("Инициализирован новый экземпляр TelegramAuth")
    
    try:
        # Сохраняем данные лота (ваш существующий код)
        with open('/data/lots.json', 'r+', encoding='utf8') as f:
            data = json.load(f)
            data[str(num)] = {
                'country': data.get(str(num), {}).get('country', ''),
                'otlega': data.get(str(num), {}).get('otlega', ''),
                'pass': data.get(str(num), {}).get('pass', ''),
                'type': 'Автоматический',
                'price': data.get(str(num), {}).get('price', 0),
                'status': 'Активен',
                'buyer': ''
            }
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # Запускаем авторизацию
        Thread(
            target=bot.tg_auth.start_auth,
            args=(num, call.from_user.id),
            daemon=True
        ).start()
        
        bot.send_message(call.from_user.id, "🚀 Запущен процесс авторизации...")
        
    except Exception as e:
        print(f"Ошибка в auto: {e}")
        bot.send_message(call.from_user.id, f"❌ Ошибка: {str(e)}")
        
    

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('waiting_code') or user_states.get(m.chat.id, {}).get('waiting_password'))
def handle_auth(message):
    chat_id = message.chat.id
    user_data = user_states.get(chat_id, {})
    text = message.text.strip()
    
    def process_auth():
        if user_data.get('waiting_code'):
            # Обработка кода подтверждения
            if tg_auth.confirm_code(chat_id, text):
                bot.send_message(chat_id, "✅ Код подтвержден!")
            else:
                if user_states.get(chat_id, {}).get('waiting_password'):
                    # Теперь ожидаем пароль 2FA (сообщение уже отправлено в confirm_code)
                    pass
                else:
                    bot.send_message(chat_id, "❌ Неверный код или ошибка авторизации")
        
        elif user_data.get('waiting_password'):
            # Обработка пароля 2FA
            if tg_auth.confirm_password(chat_id, text):
                bot.send_message(chat_id, "✅ Авторизация успешна! Сессия сохранена.")
            else:
                bot.send_message(chat_id, "❌ Неверный пароль или ошибка авторизации")
    
    Thread(target=process_auth).start()


@bot.callback_query_handler(func=lambda call: call.data.startswith('Ручной'))
def hand(call: types.CallbackQuery):
    num = call.data.replace('Ручной', '')
    try:
        with open('/data/lots.json', 'r', encoding='utf8')as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    with open('/data/lots.json', 'w', encoding='utf8')as x:
        data[str(num)] = {
            'country': data[str(num)]['country'],
            'otlega': data[str(num)]['otlega'],
            'pass': data[str(num)]['pass'],
            'type': 'Ручной',
            'price': data[str(num)]['price'],
            'status': 'Активен',
            'buyer': ''
        }
        json.dump(data, x, ensure_ascii=False, indent=4)
    bot.send_message(chat_id=call.from_user.id, text='Супер, настройка завершена, выставляю лот в каталог...')



@bot.callback_query_handler(func=lambda call: call.data=='➕ Добавить номер')
def addnumber(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "➕ Добавить номер")
    x = bot.send_message(chat_id=call.from_user.id, text=f'*Пришлите номер телефона*', parse_mode='Markdown')
    bot.register_next_step_handler(x, numbernextstep)
    

@bot.callback_query_handler(func=lambda call: call.data=='🛠 Поддержка')
def support(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "🛠 Поддержка")
    x = bot.send_message(chat_id=call.from_user.id, text=f'*Опишите вашу проблему и я отправлю ее модератору*', parse_mode='Markdown')
    bot.register_next_step_handler(x, support_next_step)

@bot.callback_query_handler(func=lambda call: call.data=='➕ Пополнить баланс')
def balance(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "➕ Пополнить баланс")
    mrk = types.InlineKeyboardMarkup(row_width=1)
    crypto = types.InlineKeyboardButton(text='Crypto Pay', callback_data='Crypto Pay')
    paymaster = types.InlineKeyboardButton(text='Карта РФ', callback_data='Карта РФ')
    mrk.row(crypto, paymaster)
    bot.send_message(call.from_user.id, '⚡ *Выберите способ оплаты*', parse_mode='Markdown', reply_markup=mrk)

@bot.callback_query_handler(func=lambda call: call.data=='Карта РФ')
def cryptopay(call:types.CallbackQuery):
    bot.answer_callback_query(call.id, "Карта РФ")
    x = bot.send_message(chat_id=call.from_user.id, text=f'*Пришлите сумму пополнения баланса* (в рублях)\n_пример_: 5.0', parse_mode='Markdown')
    bot.register_next_step_handler(x, next_step_card)

@bot.callback_query_handler(func=lambda call: call.data=='Crypto Pay')
def cardtopay(call:types.CallbackQuery):
    bot.answer_callback_query(call.id, "Crypto Pay")
    x = bot.send_message(chat_id=call.from_user.id, text=f'*Пришлите сумму пополнения баланса* (в USDT)\n_пример_: 5.0', parse_mode='Markdown')
    bot.register_next_step_handler(x, create_invoice)



@bot.callback_query_handler(func=lambda call: call.data.startswith('оплатил'))
def accept(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "Проверяю...")
    try:
        invoice = crypto.get_invoices(invoice_ids=call.data.replace('оплатил', ''))
        if str(invoice['items'][0]['invoice_id']) == str(call.data.replace('оплатил', '')):
            if invoice['items'][0]['status'] == 'paid':
                if not checkinvoice(invoice['items'][0]['invoice_id']):
                    paid(invoice['items'][0]['invoice_id'])
                    amount = float(invoice['items'][0]['amount']) * 74
                    amount = round(amount, 2)
                    mess = bot.send_message(chat_id=call.from_user.id, text='*Счет оплачен!*\n_Пополняю баланс..._', parse_mode='Markdown')
                    update_balance(user_id=str(call.from_user.id), amount_to_add=amount)
                    bot.edit_message_text(text=f'_На ваш баланс было зачисленно_ *{amount}₽*', parse_mode='Markdown', chat_id=call.from_user.id, message_id=mess.message_id)  
                    time.sleep(1)
                else: 
                    bot.send_message(chat_id=call.from_user.id, text=f'чек *{invoice['items'][0]['invoice_id']}* уже зачислен вам на баланс!', parse_mode='Markdown')
            else:
                bot.send_message(chat_id=call.from_user.id, text='*Вы не оплатили счет!*', parse_mode='Markdown')
           
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.from_user.id, text=f'ошибка с чеком *{invoice['items'][0]['invoice_id']}*', parse_mode='Markdown')
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('✅ Пополнить баланс'))       
def apply(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "✅ Пополнить баланс")
    userid = call.data.replace('✅ Пополнить баланс', '')
    with open('/data/cards.json', 'r', encoding='utf8')as f:
        data = json.load(f)
    amount = data[str(userid)]['amount']
    update_balance(user_id=str(userid), amount_to_add=amount)
    remove_dict_from_json(key_to_remove=str(userid))
    mrk = types.InlineKeyboardMarkup(row_width=1)
    but5  = types.InlineKeyboardButton(text='🖥 Главное меню', callback_data='🖥 Главное меню')
    mrk.add(but5)
    mes = bot.send_message(chat_id=userid, text=f'На ваш баланс было зачисленно *{amount}*\nУдачных покупок!', parse_mode='Markdown',reply_markup=mrk)
    current_message.update({str(userid): mes.message_id})

@bot.callback_query_handler(func=lambda call: call.data.startswith('❌ Чек не корректный'))       
def decline(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, "❌ Чек не корректный")
    userid = call.data.replace('❌ Чек не корректный', '')
    remove_dict_from_json(key_to_remove=str(userid))
    bot.send_message(chat_id=userid, text='*Модератор не подтвердил валидность чека. Баланс не был пополнен. Попробуйте еще раз*', parse_mode='Markdown')

@bot.message_handler(['get'])
def get(m: types.Message):
    for id in ADMINID:
        if m.from_user.id == id:
            try:
                for file in os.listdir('/data'):
                    with open(file, 'r', encoding='utf8')as f:
                        bot.send_document(chat_id=m.from_user.id, document=f, caption=f'{file}')
            except:
                for file in os.listdir('data'):
                    with open(file, 'r', encoding='utf8')as f:
                        bot.send_document(chat_id=m.from_user.id, document=f, caption=f'{file}')
            



bot.infinity_polling(logger_level=logging.INFO)

