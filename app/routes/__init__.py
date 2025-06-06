from fastapi import APIRouter
from .tender_routes import router as tender_router
from .compatibility_routes import router as compatibility_router

api_router = APIRouter()
api_router.include_router(tender_router)
api_router.include_router(compatibility_router)
