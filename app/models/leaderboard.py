from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class LeaderboardEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int]= Field(default=None, foreign_key="user.id", index=True)
    username: Optional[str]= Field(default=None)
    strategy_id: Optional[int] = Field(default=None, foreign_key="strategy.id", index=True)
    strategy_name: Optional[str] = Field(default=None)
    dataset: Optional[str] = Field(default="default")
    run_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    return_pct: float = Field(default=0.0)
    sharpe: Optional[float] = Field(default=None)
    max_drawdown: Optional[float] = Field(default=None)
    score: float = Field(default=0.0)
    notes: Optional[str] = Field(default=None)