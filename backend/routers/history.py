from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_history():
    return {"events": []}