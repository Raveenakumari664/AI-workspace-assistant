from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.agent import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):
    ai_response = run_agent(request.message)
    return {"response": ai_response}