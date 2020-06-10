from fastapi import FastAPI

from src.routers import health_router
from src.routers import indy_router

app = FastAPI()

app.include_router(
    indy_router.router,
    prefix="/api/v1",
    tags=["indy"]
)

app.include_router(
    health_router.router,
    tags=["healthcheck"]
)
