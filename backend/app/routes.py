from fastapi import APIRouter, Depends, HTTPException, status

from .dependencies import get_current_enterprise_id, get_current_user
from .schemas import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentResponse,
    EnterpriseProfileResponse,
    EnterpriseProfileUpdate,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from .security import create_access_token, verify_password
from .store import store

router = APIRouter(tags=["Subsystem 1 - Authentication & Enterprise"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = store.get_user_by_email(payload.email.lower())
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    enterprise = store.get_enterprise(user["enterprise_id"])
    token = create_access_token({
        "sub": user["email"],
        "enterprise_id": user["enterprise_id"],
        "role": user["role"],
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        enterprise_id=user["enterprise_id"],
        email=user["email"],
        company_name=enterprise["company_name"] if enterprise else None,
    )


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    try:
        created = store.create_enterprise(
            email=payload.email,
            password=payload.password,
            company_name=payload.company_name,
            industry=payload.industry,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    enterprise = created["enterprise"]
    user = created["user"]
    token = create_access_token({
        "sub": user["email"],
        "enterprise_id": enterprise["enterprise_id"],
        "role": user["role"],
    })

    return RegisterResponse(
        message="Enterprise registered successfully",
        enterprise_id=enterprise["enterprise_id"],
        access_token=token,
        token_type="bearer",
    )


@router.get("/profile", response_model=EnterpriseProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    enterprise = store.get_enterprise(current_user["enterprise_id"])
    if enterprise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise profile not found",
        )

    return EnterpriseProfileResponse(
        enterprise_id=enterprise["enterprise_id"],
        company_name=enterprise["company_name"],
        industry=enterprise["industry"],
        address=enterprise.get("address"),
        city=enterprise.get("city"),
        state=enterprise.get("state"),
        postal_code=enterprise.get("postal_code"),
        country=enterprise.get("country"),
        website=enterprise.get("website"),
        phone=enterprise.get("phone"),
    )


@router.put("/profile", response_model=EnterpriseProfileResponse)
def update_profile(
    payload: EnterpriseProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    enterprise_id = current_user["enterprise_id"]
    updates = payload.model_dump(exclude_unset=True)

    try:
        enterprise = store.update_enterprise(enterprise_id, updates)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return EnterpriseProfileResponse(
        enterprise_id=enterprise["enterprise_id"],
        company_name=enterprise["company_name"],
        industry=enterprise["industry"],
        address=enterprise.get("address"),
        city=enterprise.get("city"),
        state=enterprise.get("state"),
        postal_code=enterprise.get("postal_code"),
        country=enterprise.get("country"),
        website=enterprise.get("website"),
        phone=enterprise.get("phone"),
    )


@router.get("/departments", response_model=DepartmentListResponse)
def list_departments(current_enterprise_id: str = Depends(get_current_enterprise_id)):
    departments = store.list_departments(current_enterprise_id)
    return DepartmentListResponse(
        departments=[
            DepartmentResponse(
                department_id=item["department_id"],
                enterprise_id=item["enterprise_id"],
                name=item["name"],
                description=item.get("description"),
            )
            for item in departments
        ]
    )


@router.post("/departments", response_model=DepartmentResponse)
def create_department(
    payload: DepartmentCreate,
    current_enterprise_id: str = Depends(get_current_enterprise_id),
):
    department = store.create_department(
        enterprise_id=current_enterprise_id,
        name=payload.name,
        description=payload.description,
    )
    return DepartmentResponse(
        department_id=department["department_id"],
        enterprise_id=department["enterprise_id"],
        name=department["name"],
        description=department.get("description"),
    )
