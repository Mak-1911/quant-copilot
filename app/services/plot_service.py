import backtrader as bt 
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from app.utility.validators import validate_strategy_code

def generate_backtest_plot(strategy_code:str, ticker:str):
    validation = validate_strategy_code(strategy_code)
    if not validation["valid"]:
        return {"error": validation["reason"]}
    local_vars = {}
    try:
        exec(strategy_code, globals(), local_vars)
        strategy_class = next(
            (v for v in local_vars.values() if isinstance(v, type) and issubclass(v, bt.Strategy)),
            None
        )
        if not strategy_class:
            return {"error": "No valid Strategy class found."}
        df = yf.download(ticker, period="1y", progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df = df.rename(columns=lambda x: x.capitalize())  # Ensures 'open', 'close' become 'Open', etc.

        if df is None or df.empty:
            return {"error": f"No data returned for ticker: {ticker}"}

        # Backtrading Setup
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class)
        cerebro.broker.setcash(100000)
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

        result = cerebro.run()
        returns = result[0].analyzers.returns.get_analysis()
        drawdown = result[0].analyzers.drawdown.get_analysis()

        # Create equity curve
        ret_series = pd.Series(returns).cumsum()
        equity = 100000 * (1 + ret_series)

        # Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=equity, name="Equity Curve"))
        fig.update_layout(
            title=f"Backtest: {ticker}",
            xaxis_title="Days",
            yaxis_title="Equity Value",
            template="plotly_dark"
        )

        return fig.to_dict() 
        
    except Exception as e:
        return {"error": f"Plot generation failed: {str(e)}"}