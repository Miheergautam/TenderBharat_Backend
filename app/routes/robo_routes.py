from pydantic import BaseModel
from fastapi import APIRouter,Request
from app.controllers import robo_controller
from app.services.robo import tender_specific_service

class RoboRequest(BaseModel):
    user_query: str


class TenderSpecificRequest(BaseModel):
    user_query: str
    tender_id: str

router = APIRouter()

@router.post("/robo/ask")
async def ask_tenderrobo(payload: RoboRequest, request: Request):
    response = await robo_controller.process_query_controller(payload.user_query, request)
    return {
        "response": response,
    }

@router.post("/robo/tender/ask")
async def tender_field_qa(payload: TenderSpecificRequest, request: Request):
    response = await tender_specific_service.answer_tender_field_question(
        payload.user_query,
        payload.tender_id,
        request
    )
    return {"response": response}