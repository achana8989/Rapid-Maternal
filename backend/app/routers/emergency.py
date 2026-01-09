from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Optional

from app.schemas.emergency import EmergencyCreate  # ✅ use your existing schema
from app.websockets.manager import ConnectionManager  # your WS manager

router = APIRouter(prefix="/emergencies", tags=["Emergencies"])

# =========================
# WebSocket manager
# =========================
manager = ConnectionManager()

# =========================
# In-memory DB (temporary)
# =========================
class Emergency:
    def __init__(self, id: int, facility_id: str, emergency_type: str, note: Optional[str] = None):
        self.id = id
        self.facility_id = facility_id
        self.emergency_type = emergency_type
        self.note = note
        self.status = "active"
        self.escalation_level = 0
        self.created_at = datetime.utcnow()
        self.acknowledged_at = None
        self.acknowledged_by = None

    def dict(self):
        return self.__dict__


EMERGENCIES: List[Emergency] = []
ID_COUNTER = 1


def get_emergency(emergency_id: int) -> Optional[Emergency]:
    for e in EMERGENCIES:
        if e.id == emergency_id:
            return e
    return None


# =========================
# Routes
# =========================
@router.get("/", response_model=List[EmergencyCreate])
def list_emergencies():
    return [e.dict() for e in EMERGENCIES]


@router.post("/", response_model=EmergencyCreate, status_code=201)
async def create_emergency(payload: EmergencyCreate):
    global ID_COUNTER
    emergency = Emergency(
        id=ID_COUNTER,
        facility_id=payload.facility_id,
        emergency_type=payload.emergency_type,
        note=payload.note
    )
    ID_COUNTER += 1
    EMERGENCIES.append(emergency)

    # 🔥 broadcast new emergency
    await manager.broadcast({
        "type": "NEW_EMERGENCY",
        "data": emergency.dict()
    })

    return emergency.dict()


@router.post("/{emergency_id}/acknowledge")
async def acknowledge_emergency(emergency_id: int):
    emergency = get_emergency(emergency_id)
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")
    emergency.status = "acknowledged"
    emergency.acknowledged_at = datetime.utcnow()
    emergency.acknowledged_by = "Admin"

    await manager.broadcast({
        "type": "ACKNOWLEDGED",
        "data": emergency.dict()
    })
    return {"message": "Emergency acknowledged"}


@router.post("/{emergency_id}/escalate")
async def escalate_emergency(emergency_id: int):
    emergency = get_emergency(emergency_id)
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")
    emergency.escalation_level += 1

    await manager.broadcast({
        "type": "ESCALATION",
        "data": emergency.dict()
    })
    return {"message": "Emergency escalated", "level": emergency.escalation_level}
