from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.plot_service import generate_backtest_plot
from app.models.strategy import Strategy
from app.db import get_session
from sqlmodel import Session, select
from app.services.plot_service import generate_backtest_plot

router = APIRouter()

class PlotRequest(BaseModel):
    strategy_id: str
    ticker: str

@router.post("/plot")
def plot_backtest(request: PlotRequest, session: Session = Depends(get_session)):
    try:
        query = select(Strategy).where(Strategy.id == int(request.strategy_id))
        strategy = session.exec(query).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        plot_result = generate_backtest_plot(strategy.code, request.ticker)
        return plot_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
