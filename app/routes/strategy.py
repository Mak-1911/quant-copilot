from fastapi import APIRouter
from sqlmodel import select
from app.db import get_session
from app.models.strategy import Strategy

router = APIRouter()

@router.post("/strategy/save")
def save_strategy(strategy: Strategy):
    with get_session() as session:
        session.add(strategy)
        session.commit()
        session.refresh(strategy)
    return {"message": "Strategy saved successfully", "strategy_id": strategy.id}

@router.get("/strategy/list")
def get_strategies(strategy_id:int):
    with get_session() as session:
        results = session.exec(select(Strategy).order_by(Strategy.created_at.desc())).all()
        return results
    
@router.get("/strategy/{strategy_id}")
def get_strategy(strategy_id: int):
    with get_session() as session:
        strategy = session.get(Strategy, strategy_id)
        return strategy if strategy else {"error": "Strategy not found"}
    
@router.delete("/strategy/{strategy_id}")
def delete_strategy(strategy_id: int):
    with get_session() as session:
        strategy = session.get(Strategy, strategy_id)
        if not strategy:
            return {"error": "Not found"}
        session.delete(strategy)
        session.commit()
        return {"status": "deleted"}