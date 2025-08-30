# server/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import asyncio

# ======================
# FastAPI (API + Static)
# ======================

app = FastAPI(title="SBALO Stylist API")

# ---- Mock data for MVP ----
CATALOG = [
    {"id": "sh-001", "title": "Ботильоны SBL Noir",  "price": 12990, "img": "/img/noir.jpg",  "tags": ["офис", "осень"]},
    {"id": "sh-002", "title": "Сапоги SBL Storm",     "price": 16990, "img": "/img/storm.jpg", "tags": ["дождь", "casual"]},
    {"id": "sh-003", "title": "Лоферы SBL Grace",     "price": 11990, "img": "/img/grace.jpg", "tags": ["офис", "casual"]},
]

QUIZ = [
    {"id": "q1", "q": "Какую обувь лучше выбрать под прямые джинсы?", "a": ["Балетки", "Ботильоны на каблуке", "Угги"], "correct": 1, "tip": "Каблук вытягивает силуэт."},
    {"id": "q2", "q": "Сколько цветов оптимально в образе?",          "a": ["2-3", "5-6", "1"],                    "correct": 0, "tip": "Держим образ чистым: 2–3 цвета."},
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
    # TODO: запись в БД, генерация купона по городу/пользователю
    return {"ok": True, "coupon": "SBL5"}

@app.get("/healthz")
def health():
    return {"ok": True}

# Статика (SPA): сборка Vite копируется в server/public
# html=True — чтобы /app и любые SPA-маршруты отдавали index.html
app.mount("/", StaticFiles(directory="server/public", html=True), name="static")


# ======================
# Telegram Bot (inline WebApp button), runs in background
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

def _webapp_url() -> str:
    # Фоллбек на /app, если переменная не задана
    base = WEBAPP_URL or "/app"
    # Добавим дефолтный параметр города
    return f"{base}?city=spb"

async def _run_bot(bot, dp):
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("[BOT] webhook deleted, starting polling…", flush=True)
        await dp.start_polling(bot)
    except Exception as e:
        # Не роняем API — просто логируем
        print(f"[BOT ERROR] {e}", flush=True)

# Запускаем бота только если токен есть и валиден
if BOT_TOKEN:
    try:
        from aiogram import Bot, Dispatcher, types, F
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
        from aiogram.utils.token import validate_token

        validate_token(BOT_TOKEN)  # валидация формата токена ещё до инициализации Bot
        bot = Bot(BOT_TOKEN)
        dp = Dispatcher()

        @dp.message(F.text == "/start")
        async def start_cmd(m: types.Message):
            url = _webapp_url()
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Открыть мини-игру", web_app=WebAppInfo(url=url))
            ]])
            await m.answer(
                "Добро пожаловать в обучающую игру SBALO: уроки + практика + купоны. Поехали! 👇\n\n"
                f"Если кнопка не видна, открой ссылку вручную: {url}",
                reply_markup=kb
            )

        @dp.message(F.web_app_data)
        async def on_webapp_data(m: types.Message):
            import json
            try:
                payload = json.loads(m.web_app_data.data)
                coupon = payload.get("coupon", "SBL5")
            except Exception:
                coupon = "SBL5"
            await m.answer(
                f"Купон активирован: **{coupon}** −5%. Покажи это сообщение на кассе 🖤",
                parse_mode="Markdown"
            )

        @app.on_event("startup")
        async def _start_bot_task():
            print("[BOT] starting background task", flush=True)
            asyncio.create_task(_run_bot(bot, dp))

    except Exception as e:
        # Если токен невалидный/ошибка импорта — не запускаем бота, но API живёт
        print(f"[BOT DISABLED] {e}", flush=True)
else:
    print("[BOT DISABLED] BOT_TOKEN is empty", flush=True)
