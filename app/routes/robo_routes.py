from pydantic import BaseModel
from fastapi import APIRouter,Request
from app.controllers import robo_controller

class RoboRequest(BaseModel):
    user_query: str

router = APIRouter()

@router.post("/robo/ask")
async def ask_tenderrobo(payload: RoboRequest, request: Request):
    response = await robo_controller.process_query_controller(payload.user_query, request)
    return {
        "response": response,
    }
