from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

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

app.mount("/", StaticFiles(directory="server/public", html=True), name="static")
