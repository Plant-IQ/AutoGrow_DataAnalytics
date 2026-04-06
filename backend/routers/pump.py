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
from fastapi import APIRouter
from models import PumpStatusResponse, ErrorResponse

router = APIRouter()

@router.get("/", response_model=PumpStatusResponse)
def get_pump_status():
    # Mocked status until DB schema includes pump columns
    return PumpStatusResponse(ok=True, vibration=0.12, last_checked=datetime.utcnow())
