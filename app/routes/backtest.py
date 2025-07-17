from fastapi import APIRouter
from pydantic import BaseModel
from app.services.backtest_service import run_backtest_on_code

router = APIRouter()

class BacktestRequest(BaseModel):
    strategy_code:str
    ticker:str

@router.post("/backtest")
def backtest(request: BacktestRequest):
    results = run_backtest_on_code(request.strategy_code, request.ticker)
    return results