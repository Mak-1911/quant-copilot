from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal

class IndicatorParams(BaseModel):
    lookback: Optional[int] = Field(None, description="Lookback Window")
    threshold: Optional[float] = Field(None, description="Threshold value")
    multiplier: Optional[float] = Field(None, description="Multiplier eg. (for ATR)")

class StrategyBlock(BaseModel):
    indicator: Literal['zscore','sma', 'ema', 'rsi','atr']
    params: IndicatorParams

class StrategyBlueprint(BaseModel):
    asset: str
    entry: StrategyBlock
    exit: StrategyBlock