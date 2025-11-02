from datetime import datetime, timedelta
from typing import Dict, Any
from sqlmodel import Session, select
from app.db import get_session
from app.models.leaderboard import LeaderboardEntry
from app.services.backtest_service import run_backtest_results_only
import math

WEIGHTS = {
    "return_pct": 0.6,
    "sharpe": 0.3,
    "drawdown_penalty": 0.1  # subtract drawdown as penalty
}

def compute_score(metrics: Dict[str, Any]) -> float:
    ret = metrics.get("Total Return") or metrics.get("return_pct") or 0.0
    sharpe = metrics.get("Sharpe Ratio") or metrics.get("sharpe") or 0.0
    max_dd = metrics.get("Max Drawdown") or metrics.get("max_drawdown") or 0.0

    if abs(ret) <= 3:
        ret_pct = float(ret) * 100.0
    else:
        ret_pct = float(ret)
    
    sharpe_val = float(sharpe) if sharpe is not None else 0.0
    try:
        dd_pct = abs(float(max_dd)) * 100.0 if abs(float(max_dd)) <= 3 else abs(float(max_dd))
    except Exception:
        dd_pct = 0.0

    score = (WEIGHTS["return_pct"] * ret_pct) + (WEIGHTS["sharpe"] * sharpe_val * 10) - (WEIGHTS["drawdown_penalty"] * dd_pct)
    if math.isnan(score) or math.isinf(score):
        return 0.0
    return round(score, 4)

def submit_and_record(user, strategy_id: int, strategy_name: str, code: str, dataset: str = "default", ticker: str = "RELIANCE.NS"):
    results = run_backtest_results_only(code, ticker)
    if "error" in results:
        return {"error": results["error"]}
    
    metrics = results.get("metrics", results)
    score = compute_score(metrics)
    entry = LeaderboardEntry(
        user_id=getattr(user, "id", None) if user else None,
        username=getattr(user, "email", None) if user else None,
        strategy_id=strategy_id,
        strategy_name=strategy_name,
        dataset=dataset,
        run_at=datetime.utcnow(),
        return_pct=metrics.get("Total Return", metrics.get("return_pct", 0.0)),
        sharpe=metrics.get("Sharpe Ratio", metrics.get("sharpe")),
        max_drawdown=metrics.get("Max Drawdown", metrics.get("max_drawdown")),
        score=score
    )
    with get_session() as session:
        session.add(entry)
        session.commit()
        session.refresh(entry)

    return {"entry_id": entry.id, "metrics": metrics, "score": score}

def query_leaderboard(period: str = "daily", dataset: str = None, limit: int = 50):
    now = datetime.utcnow()
    with get_session() as session:
        if period == "daily":
            start = now - timedelta(days=1)
        elif period == "weekly":
            start = now - timedelta(days=7)
        else:
            start = None

        q = select(LeaderboardEntry)
        if start:
            q = q.where(LeaderboardEntry.run_at >= start)
        if dataset:
            q = q.where(LeaderboardEntry.dataset == dataset)

        q = q.order_by(LeaderboardEntry.score.desc())
        rows = session.exec(q.limit(limit)).all()

        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "user_id": r.user_id,
                "username": r.username,
                "strategy_id": r.strategy_id,
                "strategy_name": r.strategy_name,
                "dataset": r.dataset,
                "run_at": r.run_at.isoformat(),
                "return_pct": r.return_pct,
                "sharpe": r.sharpe,
                "max_drawdown": r.max_drawdown,
                "score": r.score
            })
        return result
