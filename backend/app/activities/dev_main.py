
from fastapi import FastAPI
from app.activities.router import router as activities_router

app = FastAPI(
    title="Carbon Activity Management API",
    description="Subsystem 2 - Independent Development",
    version="0.1.0"
)

app.include_router(activities_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "subsystem": "Carbon Activity Management"
    }
