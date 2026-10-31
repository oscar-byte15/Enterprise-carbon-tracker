
from uuid import uuid4

from pymongo import MongoClient, ReturnDocument

from app.config import settings


class MongoActivityRepository:

    def __init__(self, collection=None):
        self.client = None

        if collection is not None:
            self.collection = collection
        else:
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=3000
            )

            # Verify MongoDB connection
            self.client.admin.command("ping")

            database = self.client[settings.MONGODB_DB]

            self.collection = database["activity_records"]

        # Unique activity identifier
        self.collection.create_index(
            "id",
            unique=True
        )

        # Improve enterprise-specific queries
        self.collection.create_index([
            ("enterprise_id", 1),
            ("date", -1)
        ])

    # CREATE
    def create(
        self,
        activity: dict,
        enterprise_id: str
    ) -> dict:

        record = {
            **activity,
            "id": str(uuid4()),
            "enterprise_id": enterprise_id
        }

        self.collection.insert_one(record.copy())

        return record

    # READ ALL
    def get_all(
        self,
        enterprise_id: str
    ) -> list[dict]:

        return list(
            self.collection.find(
                {"enterprise_id": enterprise_id},
                {"_id": 0}
            )
        )

    # READ ONE
    def get_by_id(
        self,
        activity_id: str,
        enterprise_id: str
    ) -> dict | None:

        return self.collection.find_one(
            {
                "id": activity_id,
                "enterprise_id": enterprise_id
            },
            {"_id": 0}
        )

    # UPDATE
    def update(
        self,
        activity_id: str,
        activity: dict,
        enterprise_id: str
    ) -> dict | None:

        return self.collection.find_one_and_update(
            {
                "id": activity_id,
                "enterprise_id": enterprise_id
            },
            {"$set": activity},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER
        )

    # DELETE
    def delete(
        self,
        activity_id: str,
        enterprise_id: str
    ) -> bool:

        result = self.collection.delete_one({
            "id": activity_id,
            "enterprise_id": enterprise_id
        })

        return result.deleted_count > 0


activity_repository = MongoActivityRepository()
