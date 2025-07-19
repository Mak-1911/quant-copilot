from fastapi import APIRouter
from pydantic import BaseModel
from app.services.plot_service import generate_backtest_plot

router = APIRouter()

class PlotRequest(BaseModel):
    strategy_code: str
    ticker: str

@router.post("/plot")
def plot_backtest(request: PlotRequest):
    plot_json = generate_backtest_plot(request.strategy_code, request.ticker)
    return plot_json
