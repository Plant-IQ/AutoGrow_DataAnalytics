from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_pump_status():
    return {"status": "unknown", "message": "No vibration data yet"}