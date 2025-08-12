from typing import Optional, Literal, List, Union
from pydantic import BaseModel

class IndicatorParams(BaseModel):
    lookback: Optional[int] = None
    threshold: Optional[float] = None
    multiplier: Optional[float] = None


class EntryCondition(BaseModel):
    indicator: Literal["sma", "ema", "rsi", "zscore", "macd", "bollinger"]
    operator: Literal[">", "<", ">=", "<=", "crosses_above", "crosses_below"]
    value: Optional[float]
    params: IndicatorParams


class ExitCondition(BaseModel):
    indicator: Literal["sma", "ema", "rsi", "atr", "macd"]
    operator: Literal[">", "<", ">=", "<=", "crosses_above", "crosses_below"]
    value: Optional[float]
    params: IndicatorParams


class RiskManagement(BaseModel):
    stop_loss: Optional[Union[float, str]]
    take_profit: Optional[float]
    trailing_stop: Optional[float]


class StrategyBlueprint(BaseModel):
    asset: str  # e.g., "RELIANCE.NS"
    timeframe: Optional[str] = "1d"
    entry: List[EntryCondition]
    exit: List[ExitCondition]
    risk: Optional[RiskManagement] = None
    position_sizing: Optional[Literal["fixed", "percent", "risk_adjusted"]] = "fixed"
