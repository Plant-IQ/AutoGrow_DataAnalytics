from datetime import datetime
from fastapi import APIRouter

from models import PumpStatusResponse

router = APIRouter()


@router.get(
    "/",
    response_model=PumpStatusResponse,
    summary="Pump vibration status",
    description="Returns last vibration reading from the pump (mocked until hardware is connected).",
)
def get_pump_status():
    return PumpStatusResponse(ok=True, vibration=0.12, last_checked=datetime.utcnow())
