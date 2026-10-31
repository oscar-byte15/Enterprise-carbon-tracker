
from fastapi import APIRouter, HTTPException, Response, status

from .schemas import ActivityCreate
from .calculator import calculate_emissions
from .repository import activity_repository


router = APIRouter(
    prefix="/activities",
    tags=["Subsystem 2 - Carbon Activity Management"]
)


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
            status_code=422,
            detail=str(error)
        ) from error

    return {
        **activity.model_dump(mode="json"),
        "period": activity.date.strftime("%Y-%m"),
        **calculation
    }


# CREATE
@router.post("/", status_code=201)
def create_activity(activity: ActivityCreate):
    record = prepare_activity(activity)
    saved = activity_repository.create(record)

    return {
        "message": "Activity created successfully",
        "activity": saved
    }


# READ ALL
@router.get("/")
def get_activities():
    return activity_repository.get_all()


# READ ONE
@router.get("/{activity_id}")
def get_activity_by_id(activity_id: str):
    activity = activity_repository.get_by_id(activity_id)

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return activity


# UPDATE
@router.put("/{activity_id}")
def update_activity(
    activity_id: str,
    activity: ActivityCreate
):
    record = prepare_activity(activity)

    updated = activity_repository.update(
        activity_id, record
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return {
        "message": "Activity updated successfully",
        "activity": updated
    }


# DELETE
@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: str):
    deleted = activity_repository.delete(activity_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
