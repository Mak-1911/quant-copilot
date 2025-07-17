from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_strategy_code

router = APIRouter()

class PromptRequest(BaseModel):
    user_prompt: str

@router.post("/generate")
def generate(prompt: PromptRequest):
    code = generate_strategy_code(prompt.user_prompt)
    return {"generated_code": code}
