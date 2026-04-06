# from datetime import datetime
# from fastapi import APIRouter

# from models import PumpStatusResponse, ErrorResponse

# router = APIRouter()


# @router.get(
#     "/",
#     response_model=PumpStatusResponse,
#     summary="Pump vibration status",
#     description="Returns last vibration reading from the pump (mocked until hardware is connected).",
#     responses={
#         422: {"model": ErrorResponse, "description": "Validation error"},
#         500: {
#             "model": ErrorResponse,
#             "description": "Internal server error",
#             "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
#         },
#     },
# )
# def get_pump_status():
#     return PumpStatusResponse(ok=True, vibration=0.12, last_checked=datetime.utcnow())


from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import PumpStatusResponse, ErrorResponse
from db.sqlite import get_session, SensorReading

router = APIRouter()

@router.get("/", response_model=PumpStatusResponse)
def get_pump_status(session: Session = Depends(get_session)):
    latest = session.exec(select(SensorReading).order_by(SensorReading.ts.desc()).limit(1)).first()
    if latest:
        return PumpStatusResponse(
            ok=latest.pump_status == "OK" or latest.pump_status == "IDLE",
            vibration=1.0 if latest.pump_status == "OK" else 0.0,
            last_checked=latest.ts,
        )
    return PumpStatusResponse(ok=True, vibration=0.0, last_checked=datetime.utcnow())