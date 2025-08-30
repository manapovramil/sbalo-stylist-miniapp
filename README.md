# SBALO Stylist Mini App (Telegram WebApp + Bot + FastAPI)

## Deploy on Render
1) Connect repo with this `render.yaml` (Blueprints).
2) Set worker env vars:
   - `BOT_TOKEN` — your @sbalostylish_bot token
   - `WEBAPP_URL` — your web service URL + `/app`

## Local dev
Server:
  pip install -r server/requirements.txt
  uvicorn server.main:app --reload

WebApp:
  cd webapp && npm i && npm run dev
  # build into FastAPI static: npm run build

Bot:
  cd bot && pip install -r requirements.txt
  export BOT_TOKEN=xxx
  export WEBAPP_URL=http://127.0.0.1:8000/app
  python -m bot.main
