from fastapi import APIRouter

from models import StageResponse

router = APIRouter()


@router.get(
    "/",
    response_model=StageResponse,
    summary="Current growth stage",
    description="Returns current stage index/name and days elapsed in stage (mocked until live logic is wired).",
)
def get_stage():
    # TODO: replace with DB/logic
    return StageResponse(stage=2, label="Vegetative", days_in_stage=5)
