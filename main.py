
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Minsk")

API_KEY = "213b82a5c829440ab5c0f0bc8ea2f1d6"
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

def fetch_news_by_query(query, count=5):
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&sortBy=publishedAt&language=ru&apiKey={API_KEY}&pageSize={count}"
    )
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])
        if not articles:
            return ["• Новости не найдены"]
        return [f"• {a['title']}" for a in articles]
    except Exception as e:
        print(f"Ошибка при получении новостей: {e}")
        return ["• Ошибка при загрузке"]

def get_news_text():
    queries = {
        "🌍 Международные": "мир новости",
        "🇷🇺 Россия": "Россия",
        "💰 Финансы": "финансовые новости",
        "📱 Технологии": "технологии",
        "🧠 ИИ": "искусственный интеллект",
        "🤖 Роботы": "робототехника",
        "⚔️ Военная обстановка": "Украина война"
    }

    text = "🗞 <b>Новости за сегодня</b>\n\n"
    for title, query in queries.items():
        news_items = fetch_news_by_query(query)
        text += f"<b>{title}</b>\n" + "\n".join(news_items) + "\n\n"
    return text.strip()

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


