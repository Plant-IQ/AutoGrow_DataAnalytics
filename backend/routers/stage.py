from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_stage():
    return {
        "stage_index": 0,
        "name": "Germination",
        "day_elapsed": 0,
        "confirmed": False,
        "next_stage_requirements": "Wait 3 days, check soil moisture"
    }