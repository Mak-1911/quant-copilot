from fastapi import APIRouter
from pydantic import BaseModel
from app.services.explain_service import explain_strategy

router = APIRouter()

class ExplainRequest(BaseModel):
    strategy_code: str

@router.post("/explain")
def explain(request: ExplainRequest):
    explanation = explain_strategy(request.strategy_code)
    return {"explanation": explanation}