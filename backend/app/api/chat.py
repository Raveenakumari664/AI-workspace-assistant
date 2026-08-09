from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gemini_service import generate_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):
    ai_response = generate_response(request.message)
    return {"response": ai_response}