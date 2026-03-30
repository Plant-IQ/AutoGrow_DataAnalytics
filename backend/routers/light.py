from fastapi import APIRouter

from models import LightResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/",
    response_model=LightResponse,
    summary="Light spectrum recommendation",
    description="Returns the recommended spectrum/preset and light hours accumulated today (mock data).",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
        },
    },
)
def get_light():
    return LightResponse(spectrum="veg", hours_today=12.0)
