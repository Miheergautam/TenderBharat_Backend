from fastapi import APIRouter, Request
from app.models.tender import Tender
from app.controllers import tender_controller

router = APIRouter()

@router.get("/tenders")
async def get_all_tenders(request: Request):
    return await tender_controller.get_all_tenders(request)

@router.get("/tenders/{tender_id}")
async def get_tender_by_id(tender_id: str, request: Request):
    return await tender_controller.get_tender_by_id(request, tender_id)
