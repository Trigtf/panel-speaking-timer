from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os

from backend.audio.audio_stream import FakeAudioStream
from backend.timing.timer_engine import TimerEngine
from backend.api.routes import router

app = FastAPI(title="Panel Speaking Timer")

SPEAKERS = [1, 2, 3]
UPDATE_INTERVAL = 0.2  # seconds (5 fps)

# ---------- Frontend ----------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="ui")

@app.get("/ui")
def ui():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ---------- Core state ----------
engine = TimerEngine(SPEAKERS)
audio = FakeAudioStream(SPEAKERS)

clients = []  # list[WebSocket]

@app.on_event("startup")
async def startup():
    # start fake audio -> updates engine
    audio.start(engine.on_speech)

    # broadcaster: push status to all websocket clients
    async def broadcaster():
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            payload = json.dumps(engine.get_status())

            dead = []
            for ws in clients:
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead.append(ws)

            for ws in dead:
                if ws in clients:
                    clients.remove(ws)

    asyncio.create_task(broadcaster())

@app.on_event("shutdown")
def shutdown():
    audio.stop()

# ---------- WebSocket ----------
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(10)  # keep alive
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)

# ---------- API ----------
app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok"}

