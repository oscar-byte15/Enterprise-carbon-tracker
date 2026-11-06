
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_current_enterprise_id

from .schemas import ActivityCreate
from .oop import ActivityRecord, CalculationService
from .mongo_repository import activity_repository
from .exceptions import Subsystem2Error, ActivityNotFoundError


router = APIRouter(
    prefix="/activities",
    tags=["Subsystem 2 - Carbon Activity Management"]
)


# Prepare activity data and calculate CO2 emissions
def prepare_activity(activity: ActivityCreate, enterprise_id: str) -> dict:
    try:
        record = ActivityRecord(
            category=activity.category,
            activity_type=activity.type,
            amount=activity.amount,
            unit=activity.unit,
            activity_date=activity.date,
            enterprise_id=enterprise_id,
        )
        calculation = CalculationService().calculate(record)
    except (Subsystem2Error, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error)
        ) from error

    return {
        **activity.model_dump(mode="json"),
        "period": record.get_period(),
        **calculation
    }


# CREATE - Create activity for authenticated enterprise
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: ActivityCreate,
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    record = prepare_activity(activity, enterprise_id)

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
        error = ActivityNotFoundError("Activity not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return activity


# UPDATE - Update only an activity owned by the enterprise
@router.put("/{activity_id}")
def update_activity(
    activity_id: str,
    activity: ActivityCreate,
    enterprise_id: str = Depends(get_current_enterprise_id)
):
    record = prepare_activity(activity, enterprise_id)

    updated = activity_repository.update(
        activity_id,
        record,
        enterprise_id
    )

    if updated is None:
        error = ActivityNotFoundError("Activity not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

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
        error = ActivityNotFoundError("Activity not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
