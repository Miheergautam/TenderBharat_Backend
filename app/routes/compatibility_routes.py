from fastapi import APIRouter, Request, HTTPException, Query
from app.models.compatibility import CompatibilityRecord
from app.controllers import compatibility_controller

router = APIRouter()

# POST /compatibility – create with cookie auth
@router.post("/compatibility")
async def create_comp_record(request: Request, payload: CompatibilityRecord):
    return await compatibility_controller.create_compatibility_record(request, payload)

# GET /compatibility – get all records
@router.get("/compatibility")
async def get_everything(request: Request):
    return await compatibility_controller.get_all_records(request)

# GET /compatibility/filter?user_id=&tender_id=
@router.get("/compatibility/filter")
async def get_by_user_and_tender(
    request: Request,
    user_id: str = Query(...),
    tender_id: str = Query(...)
):
    return await compatibility_controller.get_by_user_and_tender(request, user_id, tender_id)

# GET /compatibility/user/{user_id}
@router.get("/compatibility/user/{user_id}")
async def get_by_user(request: Request, user_id: str):
    return await compatibility_controller.get_by_user(request, user_id)

# GET /compatibility/tender/{tender_id}
@router.get("/compatibility/tender/{tender_id}")
async def get_by_tender(request: Request, tender_id: str):
    return await compatibility_controller.get_by_tender(request, tender_id)
