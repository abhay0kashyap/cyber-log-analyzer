from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.alerts import router as alerts_router
from api.logs import router as logs_router
from api.reports import router as reports_router
from api.settings import router as settings_router
from api.stats import router as stats_router
from core.database import init_db
from ws import ws_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Cyber Log Analyzer API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats_router)
app.include_router(alerts_router)
app.include_router(logs_router)
app.include_router(reports_router)
app.include_router(settings_router)


@app.get("/")
async def root():
    return {"message": "Cyber Log Analyzer API running 🚀"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
