from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_harvest_eta():
    return {"eta_days": None, "message": "Not enough data yet"}