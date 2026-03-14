from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_light():
    return {"color": "OFF", "hours_per_day": 0, "reason": "Germination stage"}