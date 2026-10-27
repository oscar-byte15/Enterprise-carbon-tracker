
from fastapi import APIRouter, HTTPException

from .schemas import ActivityCreate
from .calculator import calculate_emissions


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.post("/")
def create_activity(activity: ActivityCreate):
    try:
        calculation = calculate_emissions(
            category=activity.category,
            activity_type=activity.type,
            amount=activity.amount,
            unit=activity.unit
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error

    return {
        "message": "Activity calculated successfully",
        "activity": {
            **activity.model_dump(mode="json"),
            **calculation
        }
    }
