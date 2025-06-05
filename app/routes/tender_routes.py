from fastapi import APIRouter, Request
from app.models.tender import Tender
from app.controllers import tender_controller

router = APIRouter()

@router.get("/tenders")
async def get_all_tenders(request: Request):
    return await tender_controller.get_all_tenders(request)
