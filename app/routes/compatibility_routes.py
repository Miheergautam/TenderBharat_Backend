from fastapi import APIRouter, Request
from app.controllers import compatibility_controller
from app.models.compatibility import CompatibilityRecord

router = APIRouter()

# POST  /compatibility  – create
@router.post("/compatibility")
async def create_record(request: Request, payload: CompatibilityRecord):
    return await compatibility_controller.create_compatibility_record(request, payload)

# GET   /compatibility/{tender_id}  – read
@router.get("/compatibility/{tender_id}")
async def get_record(tender_id: str, request: Request):
    return await compatibility_controller.get_compatibility_by_tender(request, tender_id)

# GET /compatibility – get all
@router.get("/compatibility")
async def get_all_records(request: Request):
    return await compatibility_controller.get_all_compatibility_records(request)