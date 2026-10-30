from __future__ import annotations

from typing import Any
from uuid import uuid4

from .security import hash_password


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.enterprises: dict[str, dict[str, Any]] = {}
        self.departments: dict[str, list[dict[str, Any]]] = {}

    def create_enterprise(self, email: str, password: str, company_name: str, industry: str) -> dict[str, Any]:
        normalized_email = email.lower().strip()
        if normalized_email in self.users:
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
        self.enterprises[enterprise_id] = enterprise
        self.departments.setdefault(enterprise_id, [])

        user = {
            "id": str(uuid4()),
            "email": normalized_email,
            "password_hash": hash_password(password),
            "enterprise_id": enterprise_id,
            "role": "admin",
        }
        self.users[normalized_email] = user

        return {
            "enterprise": enterprise,
            "user": user,
        }

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        return self.users.get(email.lower().strip())

    def get_enterprise(self, enterprise_id: str) -> dict[str, Any] | None:
        return self.enterprises.get(enterprise_id)

    def update_enterprise(self, enterprise_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        enterprise = self.enterprises.get(enterprise_id)
        if enterprise is None:
            raise ValueError("Enterprise not found")

        for key, value in updates.items():
            if value is not None:
                enterprise[key] = value
        return enterprise

    def list_departments(self, enterprise_id: str) -> list[dict[str, Any]]:
        return list(self.departments.get(enterprise_id, []))

    def create_department(self, enterprise_id: str, name: str, description: str | None = None) -> dict[str, Any]:
        department = {
            "department_id": str(uuid4()),
            "enterprise_id": enterprise_id,
            "name": name.strip(),
            "description": description.strip() if description else None,
        }
        self.departments.setdefault(enterprise_id, []).append(department)
        return department


store = InMemoryStore()
