# app/routers/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
clients = []


@router.websocket("/ws/emergencies")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # keep connection open; ignore incoming data
            await websocket.receive_text()
    except WebSocketDisconnect:
        try:
            clients.remove(websocket)
        except ValueError:
            pass


async def broadcast_update(message: dict | None = None):
    """Broadcast a message to connected websocket clients. If `message` is None,
    send a simple update trigger so clients can refresh via their own polling.
    """
    payload = message or {"event": "update"}
    for client in list(clients):
        try:
            await client.send_json(payload)
        except Exception:
            try:
                clients.remove(client)
            except ValueError:
                pass
