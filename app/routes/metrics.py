from datetime import datetime
from typing import List

from app.db import get_session
from app.models.strategy_metrics import StrategyMetricsModel
from app.services.backtest_service import get_strategy_returns
from app.services.metrics import PerformanceMetrics
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/{strategy_id}")
async def get_strategy_metrics(
    strategy_id: int,
    session: Session = Depends(get_session)
):
    """Get latest metrics for a strategy"""
    statement = select(StrategyMetricsModel).where(
        StrategyMetricsModel.strategy_id == strategy_id
    ).order_by(StrategyMetricsModel.calculation_date.desc())
    
    metrics = session.exec(statement).first()
    
    if not metrics: 
        raise HTTPException(status_code=404, detail="Metrics not found for the given strategy ID")
    
    return metrics

@router.post("/{strategy_id}/calculate")
async def calculate_strategy_metrics(
    strategy_id: int, 
    ticker: str = Query(default="AAPL", min_length=1, max_length=10),
    session: Session = Depends(get_session)
):
    """Calculate and store metrics for a given strategy"""
    try:
        print(f"[DEBUG] Ticker type: {type(ticker)}, value: {ticker}")
        # Pass the session to get_strategy_returns
         # Ensure ticker is properly formatted
        if not isinstance(ticker, str):
            raise ValueError("Ticker must be a string")
            
        ticker = ticker.strip().upper()
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        returns = await get_strategy_returns(strategy_id, session, ticker)
        metrics = PerformanceMetrics.calculate_metrics(returns)

        db_metrics = StrategyMetricsModel(
            strategy_id=strategy_id,
            calculation_date=datetime.utcnow(),  # Add current timestamp
            **metrics
        )
        
        session.add(db_metrics)
        session.commit()
        session.refresh(db_metrics)

        return db_metrics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{strategy_id}/returns")
async def get_strategy_returns_metrics(
    strategy_id: int,
    ticker: str = Query(default="AAPL", min_length=1, max_length=10),
    session: Session = Depends(get_session)
):
    """Calculate metrics for a strategy based on its returns"""
    try:
        print(f"[DEBUG] Ticker type: {type(ticker)}, value: {ticker}")
        # Ensure ticker is properly formatted
        if not isinstance(ticker, str):
            raise ValueError("Ticker must be a string")
            
        ticker = ticker.strip().upper()
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        # Pass the session to get_strategy_returns
        returns = await get_strategy_returns(strategy_id, session, ticker)
        metrics = PerformanceMetrics.calculate_metrics(returns)
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))