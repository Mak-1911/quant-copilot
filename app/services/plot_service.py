from fastapi import Depends, HTTPException
from typing import Optional
from app.models.strategy import Strategy
from app.db import get_session
from sqlmodel import select, Session
import backtrader as bt
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go


def generate_backtest_plot(strategy_code: str, ticker: str) -> dict:
  local_vars = {}
  try:
    print(type(ticker), ticker)
    exec(strategy_code, globals(), local_vars)
    strategy_class = next(
            (v for v in local_vars.values() if isinstance(v, type) and issubclass(v, bt.Strategy)), 
            None
        )
    print(strategy_class)
    if not strategy_class:
          raise ValueError("No valid backtrader Strategy found in code.")
    df = yf.download(ticker, period="1y")
    if df.empty:
        raise ValueError(f"No data for ticker: {ticker}")

    if isinstance(df.columns, pd.MultiIndex):
      df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
    df.columns = [str(col).lower() for col in df.columns]
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(strategy_class)
    cerebro.broker.setcash(100000)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    results = cerebro.run()
    returns = results[0].analyzers.timereturn.get_analysis()
    drawdown = results[0].analyzers.drawdown.get_analysis()

    #Creating the equity curve
    ret_series = pd.Series(returns).cumsum()
    equity_curve = (1 + ret_series) * 100000

    #plotting
    plot = go.Figure()
    plot.add_trace(go.Scatter(y=equity_curve , name="Equity Curve"))
    plot.update_layout(
            title=f"Backtest: {ticker}",
            xaxis_title="Days",
            yaxis_title="Equity Value",
            template="plotly_dark"
    )

    return plot.to_dict()
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))