from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    company_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=120)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    enterprise_id: str
    email: str
    company_name: Optional[str] = None


class EnterpriseProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    industry: Optional[str] = Field(default=None, min_length=1, max_length=120)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=120)
    state: Optional[str] = Field(default=None, max_length=120)
    postal_code: Optional[str] = Field(default=None, max_length=30)
    country: Optional[str] = Field(default=None, max_length=120)
    website: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=40)


class EnterpriseProfileResponse(BaseModel):
    enterprise_id: str
    company_name: str
    industry: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class DepartmentResponse(BaseModel):
    department_id: str
    enterprise_id: str
    name: str
    description: Optional[str] = None


class DepartmentListResponse(BaseModel):
    departments: list[DepartmentResponse]


class RegisterResponse(BaseModel):
    message: str
    enterprise_id: str
    access_token: str
    token_type: str = "bearer"
