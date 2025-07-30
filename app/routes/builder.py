from fastapi import APIRouter
from app.models.strategy_blueprint import StrategyBlueprint
from app.services.builder_service import from_blueprint_to_prompt
from app.services.llm_service import generate_strategy_code

router = APIRouter()

@router.post("/builder/translate")
def translate_blueprint(bp: StrategyBlueprint):
    prompt = from_blueprint_to_prompt(bp)
    code = generate_strategy_code(prompt)
    return {"prompt": prompt, "generated_code": code}