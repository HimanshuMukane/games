from fastapi import APIRouter
from .routes import router as frontend_router
from .game import router as game_router

api_router = APIRouter()
api_router.include_router(frontend_router)
api_router.include_router(game_router)
