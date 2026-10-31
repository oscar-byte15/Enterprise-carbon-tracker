
from uuid import uuid4
from threading import Lock


class InMemoryActivityRepository:
    def __init__(self):
        self._activities = {}
        self._lock = Lock()

    def create(self, activity: dict) -> dict:
        with self._lock:
            activity_id = str(uuid4())
            record = {
                **activity,
                "id": activity_id,
            }
            self._activities[activity_id] = record
            return record.copy()

    def get_all(self) -> list[dict]:
        with self._lock:
            return [
                record.copy()
                for record in self._activities.values()
            ]

    def get_by_id(self, activity_id: str) -> dict | None:
        with self._lock:
            record = self._activities.get(activity_id)
            return record.copy() if record else None

    def update(
        self, activity_id: str, activity: dict
    ) -> dict | None:
        with self._lock:
            if activity_id not in self._activities:
                return None

            record = {
                **activity,
                "id": activity_id,
            }
            self._activities[activity_id] = record
            return record.copy()

    def delete(self, activity_id: str) -> bool:
        with self._lock:
            return self._activities.pop(
                activity_id, None
            ) is not None


activity_repository = InMemoryActivityRepository()
