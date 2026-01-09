# backend/app/routers/ws_emergencies.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

from app.db.database import SessionLocal
from app.db.models import MaternalEmergency  # Correct model import

router = APIRouter(prefix="/ws", tags=["WebSockets"])


# --- WebSocket connection manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self.lock:
            self.active_connections.append(ws)

    async def disconnect(self, ws: WebSocket):
        async with self.lock:
            if ws in self.active_connections:
                self.active_connections.remove(ws)

    async def broadcast(self, payload: dict):
        async with self.lock:
            connections = list(self.active_connections)

        for ws in connections:
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect(ws)


# Single manager instance
manager = ConnectionManager()


# --- Data access functions ---
def fetch_emergencies():
    db = SessionLocal()
    try:
        records = db.query(MaternalEmergency).all()  # <-- FIXED
        return [
            {
                "id": e.id,
                "facility_id": e.facility_id,
                "emergency_type": e.emergency_type,
                "status": e.status,
                "note": e.note,
                "escalation_level": e.escalation_level,
                "created_at": e.created_at.isoformat(),
            }
            for e in records
        ]
    finally:
        db.close()


def get_summary(items: list[dict]):
    return {
        "total": len(items),
        "active": sum(1 for i in items if i["status"] == "active"),
        "escalated": sum(1 for i in items if i["escalation_level"] > 0),
    }


# --- WebSocket endpoint ---
@router.websocket("/emergencies")
async def emergencies_ws(ws: WebSocket):
    await manager.connect(ws)

    try:
        # Send initial state
        data = fetch_emergencies()
        await ws.send_json({
            "summary": get_summary(data),
            "emergencies": data,
        })

        # Keep connection alive
        while True:
            await ws.receive_text()  # do nothing, just keep alive

    except WebSocketDisconnect:
        await manager.disconnect(ws)


# --- Optional broadcast helper ---
async def broadcast_update():
    """
    Call this whenever emergencies change in the DB
    to update all connected WebSocket clients in real-time.
    """
    data = fetch_emergencies()
    message = {
        "summary": get_summary(data),
        "emergencies": data,
    }
    await manager.broadcast(message)
