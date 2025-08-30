import asyncio, os, json
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL is not set")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(m: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="Открыть мини-игру", web_app=WebAppInfo(url=f"{WEBAPP_URL}?city=spb")))
    await m.answer("Добро пожаловать в обучающую игру SBALO: уроки + практика + купоны. Поехали! 👇", reply_markup=kb)

@dp.message(F.web_app_data)
async def on_webapp_data(m: types.Message):
    try:
        payload = json.loads(m.web_app_data.data)
        coupon = payload.get("coupon", "SBL5")
    except Exception:
        coupon = "SBL5"
    await m.answer(f"Купон активирован: **{coupon}** −5%. Покажи это сообщение на кассе 🖤", parse_mode="Markdown")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
