from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_emergencies():
    return {"status": "Emergency router working"}
