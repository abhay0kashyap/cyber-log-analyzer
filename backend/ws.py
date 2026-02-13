from __future__ import annotations

from fastapi import WebSocket


class LiveWebSocketManager:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict) -> None:
        stale: list[WebSocket] = []
        for conn in self.connections:
            try:
                await conn.send_json(payload)
            except Exception:
                stale.append(conn)

        for conn in stale:
            self.disconnect(conn)


ws_manager = LiveWebSocketManager()
