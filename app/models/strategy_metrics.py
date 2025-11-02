from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class StrategyMetricsModel(SQLModel, table=True):
    __tablename__ = "strategy_metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    strategy_id: int = Field(foreign_key="strategy.id")
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    calmar_ratio: float
    profit_factor: float
    recovery_factor: float
    trades_per_month: float

