
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_current_enterprise_id

from .schemas import ActivityCreate
from .calculator import calculate_emissions
from .mongo_repository import activity_repository


router = APIRouter(
    prefix="/activities",
    tags=["Subsystem 2 - Carbon Activity Management"]
)


# Prepare activity data and calculate CO2 emissions
def prepare_activity(activity: ActivityCreate) -> dict:
    try:
        calculation = calculate_emissions(
            category=activity.category,
            activity_type=activity.type,
            amount=activity.amount,
            unit=activity.unit
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error)
        ) from error

    return {
        **activity.model_dump(mode="json"),
        "period": activity.date.strftime("%Y-%m"),
        **calculation
    }


# CREATE - Create activity for authenticated enterprise
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: ActivityCreate,
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    record = prepare_activity(activity)

    saved = activity_repository.create(
        record,
        enterprise_id
    )

    return {
        "message": "Activity created successfully",
        "activity": saved
    }


# READ ALL - Get only activities belonging to the enterprise
@router.get("/")
def get_activities(
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    return activity_repository.get_all(enterprise_id)


# READ ONE - Get activity belonging to the enterprise
@router.get("/{activity_id}")
def get_activity_by_id(
    activity_id: str,
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    activity = activity_repository.get_by_id(
        activity_id,
        enterprise_id
    )

    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity


# UPDATE - Update only an activity owned by the enterprise
@router.put("/{activity_id}")
def update_activity(
    activity_id: str,
    activity: ActivityCreate,
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    record = prepare_activity(activity)

    updated = activity_repository.update(
        activity_id,
        record,
        enterprise_id
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return {
        "message": "Activity updated successfully",
        "activity": updated
    }


# DELETE - Delete only an activity owned by the enterprise
@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_activity(
    activity_id: str,
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    deleted = activity_repository.delete(
        activity_id,
        enterprise_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
