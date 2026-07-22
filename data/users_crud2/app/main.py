"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="Users CRUD API",
    description="REST API for managing users with CRUD operations",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users_router, prefix="/api/v1")
