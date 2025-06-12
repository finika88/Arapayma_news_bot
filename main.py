
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Minsk")

CHAT_IDS_FILE = "chat_ids.txt"

def add_chat_id(chat_id: int):
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            ids = set(map(int, f.read().splitlines()))
    except FileNotFoundError:
        ids = set()
    ids.add(chat_id)
    with open(CHAT_IDS_FILE, "w") as f:
        for cid in ids:
            f.write(str(cid) + "\n")

def get_chat_ids():
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            return list(map(int, f.read().splitlines()))
    except FileNotFoundError:
        return []

def get_news_text() -> str:
    return (
        "🗞 <b>Новости за сегодня</b>\n\n"
        "<b>🌍 Международные</b>\n• 1\n• 2\n• 3\n• 4\n• 5\n\n"
        "<b>🇷🇺 Россия</b>\n• 1\n• 2\n• 3\n• 4\n• 5\n\n"
        "<b>💰 Финансы</b>\n• 1\n• 2\n• 3\n• 4\n• 5\n\n"
        "<b>📱 Технологии</b>\n• 1\n• 2\n• 3\n• 4\n• 5\n\n"
        "<b>🧠 ИИ</b>\n• 1\n• 2\n• 3\n• 4\n• 5\n\n"
        "<b>🤖 Роботы</b>\n• 1\n• 2\n• 3\n• 4\n• 5\n\n"
        "<b>⚔️ Военная обстановка</b>\n• 1\n• 2\n• 3\n• 4\n• 5"
    )

@dp.message(lambda message: message.text == "/start")
async def start(message: Message):
    add_chat_id(message.chat.id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕒 Новости сейчас", callback_data="news_now")]
        ]
    )
    await message.answer(
        "✅ Бот активен. Новости будут приходить каждый день в 23:59.\n\n"
        "А если хочешь — нажми кнопку ниже:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "news_now")
async def handle_news_now(callback_query: CallbackQuery):
    await callback_query.message.answer(get_news_text(), parse_mode="HTML")
    await callback_query.answer()

async def send_news():
    text = get_news_text()
    for chat_id in get_chat_ids():
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка отправки в чат {chat_id}: {e}")

async def scheduler_task():
    scheduler.add_job(send_news, "cron", hour=23, minute=59)
    scheduler.start()

async def main():
    await scheduler_task()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
