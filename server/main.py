from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os, asyncio

# === API ===
app = FastAPI(title="SBALO Stylist API")

CATALOG = [
    {"id":"sh-001","title":"Ботильоны SBL Noir","price":12990,"img":"/img/noir.jpg","tags":["офис","осень"]},
    {"id":"sh-002","title":"Сапоги SBL Storm","price":16990,"img":"/img/storm.jpg","tags":["дождь","casual"]},
    {"id":"sh-003","title":"Лоферы SBL Grace","price":11990,"img":"/img/grace.jpg","tags":["офис","casual"]},
]
QUIZ = [
    {"id":"q1","q":"Какую обувь лучше выбрать под прямые джинсы?","a":["Балетки","Ботильоны на каблуке","Угги"],"correct":1,"tip":"Каблук вытягивает силуэт."},
    {"id":"q2","q":"Сколько цветов оптимально в образе?","a":["2-3","5-6","1"],"correct":0,"tip":"Держим образ чистым: 2-3 цвета."},
]

class MissionResult(BaseModel):
    user_id: int
    look_items: List[str]
    city: str

@app.get("/api/catalog")
def catalog():
    return CATALOG

@app.get("/api/quiz")
def quiz():
    return QUIZ

@app.post("/api/mission/submit")
def submit(res: MissionResult):
    return {"ok": True, "coupon": "SBL5"}

@app.get("/healthz")
def health():
    return {"ok": True}

# Статика: собранный фронт
app.mount("/", StaticFiles(directory="server/public", html=True), name="static")

# === Telegram Bot в том же процессе ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

if BOT_TOKEN:
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(F.text == "/start")
    async def start(m: types.Message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        url = (WEBAPP_URL or "/app") + "?city=spb"
        kb.add(KeyboardButton(text="Открыть мини-игру", web_app=WebAppInfo(url=url)))
        await m.answer("Добро пожаловать в обучающую игру SBALO: уроки + практика + купоны. Поехали! 👇", reply_markup=kb)

    @dp.message(F.web_app_data)
    async def on_webapp_data(m: types.Message):
        import json
        try:
            payload = json.loads(m.web_app_data.data)
            coupon = payload.get("coupon", "SBL5")
        except Exception:
            coupon = "SBL5"
        await m.answer(f"Купон активирован: **{coupon}** −5%. Покажи это сообщение на кассе 🖤", parse_mode="Markdown")

    @app.on_event("startup")
    async def _start_bot():
        # Убедимся, что long polling не блокирует uvicorn
        asyncio.create_task(_run_bot())

    async def _run_bot():
        # Сбросим вебхук на всякий случай и стартанём polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
