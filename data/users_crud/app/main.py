from fastapi import FastAPI

from app.routers.user_router import router

app = FastAPI(title="Users CRUD API", version="1.0.0")

app.include_router(router)
