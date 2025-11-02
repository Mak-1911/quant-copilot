from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.services.leaderboard_service import submit_and_record, query_leaderboard
from app.auth.utils import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/leaderboard")

class SubmitRequest(BaseModel):
    strategy_id: Optional[int]
    strategy_name: Optional[str]
    code: str
    dataset: Optional[str] = "default"
    ticker: Optional[str] = "RELIANCE.NS"

@router.post("/submit")
def submit_result(req: SubmitRequest, current_user = Depends(get_current_user)):
    res = submit_and_record(current_user, req.strategy_id, req.strategy_name or "unnamed", req.code, req.dataset, req.ticker)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


@router.get("/top")
def get_top(period: Optional[str] = Query("daily", regex="^(daily|weekly|alltime)$"), dataset: Optional[str] = None, limit: int = 50):
    return {"period": period, "dataset": dataset, "top": query_leaderboard(period=period, dataset=dataset, limit=limit)}