from fastapi import APIRouter
from .lots import lot_router
from .ws import ws_router

global_router = APIRouter()
global_router.include_router(lot_router)
global_router.include_router(ws_router)
