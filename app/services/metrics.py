import numpy as np 
import pandas as pd 
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class StrategyMetrics:
    strategy_id: int
    calculation_date: datetime
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

class PerformanceMetrics:
    @staticmethod
    def calculate_metrics(returns: pd.Series) -> Dict[str, Any]:
        """ Calculating Comprehensive Strategy Performance Metrics """
        annual_factor = 252 #Since 252 trading days in a year

        """Basic Metrics"""
        total_returns = (returns + 1).prod() - 1
        daily_returns = returns.mean()
        volatility = returns.std() * np.sqrt(annual_factor)

        """Risk-Adjusted Metrics"""
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()  # Get the maximum drawdown as a scalar
        
        sharpe = (daily_returns * annual_factor) / volatility if volatility != 0 else 0.0
        sortino = (daily_returns * annual_factor) / (returns[returns < 0].std() * np.sqrt(annual_factor)) if returns[returns < 0].std() != 0 else 0.0

        """Trading Metrics"""
        winning_days = len(returns[returns > 0])
        losing_days = len(returns[returns < 0])
        win_rate = winning_days / (winning_days + losing_days ) if (winning_days + losing_days) > 0 else 0

        
        return {
            "total_return": float(total_returns) if not np.isnan(total_returns) else 0.0,
            "annual_return": float((1 + total_returns) ** (annual_factor / len(returns)) - 1) if not np.isnan((1 + total_returns) ** (annual_factor / len(returns)) - 1) else 0.0,
            "volatility": float(volatility) if not np.isnan(volatility) else 0.0,
            "sharpe_ratio": float(sharpe) if not np.isnan(sharpe) else 0.0,
            "sortino_ratio": float(sortino) if not np.isnan(sortino) else 0.0,
            "max_drawdown": float(max_drawdown) if not np.isnan(max_drawdown) else 0.0,
            "win_rate": float(win_rate) if not np.isnan(win_rate) else 0.0,
            "avg_win": float(returns[returns > 0].mean()) if len(returns[returns > 0]) > 0 and not np.isnan(returns[returns > 0].mean()) else 0.0,
            "avg_loss": float(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 and not np.isnan(returns[returns < 0].mean()) else 0.0,
            # Set default values for fields that are in the model but not calculated here
            "calmar_ratio": 0.0,
            "profit_factor": 0.0,
            "recovery_factor": 0.0,
            "trades_per_month": 0.0
        }