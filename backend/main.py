from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import os
import threading
from typing import List

from backend.timing.timer_engine import TimerEngine

# =========================
# Config
# =========================
# Το TimerEngine χρειάζεται ένα αρχικό set speaker IDs.
# Στο diarization θα δημιουργούνται clusters 1..N δυναμικά, αλλά κρατάμε ένα "seed".
SEED_SPEAKERS = [1, 2, 3, 4, 5, 6]
UPDATE_INTERVAL = 0.2  # seconds (5 fps)


# =========================
# STRICT import: diarization is required
# =========================
try:
    from backend.diarization.diarization_engine import DiarizationEngine  # απαιτείται
except Exception as e:
    raise RuntimeError(
        "Diarization mode is REQUIRED but could not be imported.\n"
        "Fix: make sure backend/diarization/diarization_engine.py exists and local deps are installed.\n"
        f"Import error: {e}"
    )


app = FastAPI(title="Panel Speaking Timer (Diarization Only)")

# ---------- Frontend mount ----------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="ui")

@app.get("/ui")
def ui():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/")
def root():
    return {"status": "ok", "mode": "diarization_only"}

# ---------- Core state ----------
engine = TimerEngine(SEED_SPEAKERS)
clients: List[WebSocket] = []

# Θα τρέχει σε background thread
diar: DiarizationEngine | None = None
diar_thread: threading.Thread | None = None


@app.on_event("startup")
async def startup():
    global diar, diar_thread

    # 1) Start diarization engine (STRICT: no fallback)
    diar = DiarizationEngine(engine.on_speech)

    def run_diar():
        # Αν κρασάρει, θέλουμε να το δούμε καθαρά στο console.
        # (Σε production θα κάναμε restart/recovery, αλλά εδώ είμαστε strict.)
        diar.start()

    diar_thread = threading.Thread(target=run_diar, daemon=True)
    diar_thread.start()

    # 2) WebSocket broadcaster
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
    # Προσπαθούμε να σταματήσουμε καθαρά το mic stream
    if diar is not None:
        try:
            diar.stop()
        except Exception:
            pass


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
