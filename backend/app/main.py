from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.activities.router import router as activities_router
from app.routes import router as auth_router

app = FastAPI(
    title="Enterprise Carbon Tracker API",
    description="Authentication, Enterprise Management, and Carbon Activity APIs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(activities_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "enterprise-carbon-tracker",
    }
