
from typing import Any
from uuid import uuid4

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError

from .config import settings
from .security import hash_password


class MongoStore:
    def __init__(self, database=None):
        self.client = None

        if database is None:
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=3000,
            )
            self.client.admin.command("ping")
            database = self.client[settings.MONGODB_DB]

        self.users = database["users"]
        self.enterprises = database["enterprises"]
        self.departments = database["departments"]

        # Unique identifiers
        self.users.create_index("email", unique=True)
        self.enterprises.create_index("enterprise_id", unique=True)
        self.departments.create_index("department_id", unique=True)

        # Improve enterprise-specific queries
        self.departments.create_index("enterprise_id")

    def create_enterprise(
        self,
        email: str,
        password: str,
        company_name: str,
        industry: str,
    ) -> dict[str, Any]:
        normalized_email = email.lower().strip()

        if self.users.find_one({"email": normalized_email}):
            raise ValueError("Email is already registered")

        enterprise_id = str(uuid4())

        enterprise = {
            "enterprise_id": enterprise_id,
            "company_name": company_name.strip(),
            "industry": industry.strip(),
            "address": None,
            "city": None,
            "state": None,
            "postal_code": None,
            "country": None,
            "website": None,
            "phone": None,
        }

        user = {
            "id": str(uuid4()),
            "email": normalized_email,
            "password_hash": hash_password(password),
            "enterprise_id": enterprise_id,
            "role": "admin",
        }

        # Create the enterprise first, then its admin user.
        # Clean up the enterprise if user creation fails.
        self.enterprises.insert_one(enterprise.copy())

        try:
            self.users.insert_one(user.copy())
        except DuplicateKeyError as exc:
            self.enterprises.delete_one({
                "enterprise_id": enterprise_id
            })
            raise ValueError(
                "Email is already registered"
            ) from exc
        except Exception:
            self.enterprises.delete_one({
                "enterprise_id": enterprise_id
            })
            raise

        return {
            "enterprise": enterprise,
            "user": user,
        }

    def get_user_by_email(
        self, email: str
    ) -> dict[str, Any] | None:
        return self.users.find_one(
            {"email": email.lower().strip()},
            {"_id": 0},
        )

    def get_enterprise(
        self, enterprise_id: str
    ) -> dict[str, Any] | None:
        return self.enterprises.find_one(
            {"enterprise_id": enterprise_id},
            {"_id": 0},
        )

    def update_enterprise(
        self,
        enterprise_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        valid_updates = {
            key: value
            for key, value in updates.items()
            if value is not None
        }

        if not valid_updates:
            enterprise = self.get_enterprise(enterprise_id)
        else:
            enterprise = self.enterprises.find_one_and_update(
                {"enterprise_id": enterprise_id},
                {"$set": valid_updates},
                projection={"_id": 0},
                return_document=ReturnDocument.AFTER,
            )

        if enterprise is None:
            raise ValueError("Enterprise not found")

        return enterprise

    def list_departments(
        self, enterprise_id: str
    ) -> list[dict[str, Any]]:
        return list(
            self.departments.find(
                {"enterprise_id": enterprise_id},
                {"_id": 0},
            )
        )

    def create_department(
        self,
        enterprise_id: str,
        name: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        department = {
            "department_id": str(uuid4()),
            "enterprise_id": enterprise_id,
            "name": name.strip(),
            "description": (
                description.strip() if description else None
            ),
        }

        self.departments.insert_one(department.copy())

        return department
