from datetime import datetime
from fastapi import APIRouter
from models import HistoryResponse

router = APIRouter()

@router.get("/", response_model=HistoryResponse)
def get_history():
    # Mock empty history until schema/data is aligned
    return HistoryResponse(points=[])
