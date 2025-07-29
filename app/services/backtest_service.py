import backtrader as bt
import yfinance as yf
import numpy as np
import pandas as pd
from app.utility.validators import validate_strategy_code

def calculate_cagr(initial_value, final_value, periods):
    return ((final_value / initial_value) ** (1 / periods)) - 1

def calculate_sharpe_ratio(returns):
    return np.mean(returns)/np.std(returns) * np.sqrt(252)  if np.std(returns) else 0

def run_backtest_on_code(strategy_code: str, ticker: str):
    local_vars = {}
    try:
        exec(strategy_code, globals(), local_vars)
        strategy_class = next(
            (v for v in local_vars.values() if isinstance(v, type) and issubclass(v, bt.Strategy)), 
            None
        )
        if not strategy_class:
            return {"error": "No valid backtrader Strategy found in code."}

        df = yf.download(ticker, period="1y")
        if df.empty:
            return {"error": f"No data for ticker: {ticker}"}

        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class)
        cerebro.broker.setcash(100000)

        start_value = cerebro.broker.getvalue()
        cerebro.run()
        end_value = cerebro.broker.getvalue()

        return {
            "start_value": start_value,
            "end_value": end_value,
            "pnl": end_value - start_value
        }
    except Exception as e:
        return {"error": str(e)}

def run_backtest_results_only(strategy_code:str, ticker:str):
    validation = validate_strategy_code(strategy_code)
    if not validation["valid"]:
        return {"error": validation["message"]}
    
    local_vars = {}
    try:
        exec(strategy_code, globals(), local_vars)
        strategy_class = next(
            (v for v in local_vars.values() if isinstance(v, type) and issubclass(v, bt.Strategy)), 
        )
        if not strategy_class:
            return {"error":"No valid Strategy Class"}
        
        df = yf.download(ticker, period="1y")
        if isinstance(df.columns, pd.MultIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(100000)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class)

        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        results = cerebro.run()
        r = results[0]

        metrics = {
            "Share Ratio": r.analyzers.sharpe.get_analysis().get('sharperatio', None),
            "Max Drawdown": r.analyzers.drawdown.get_analysis().get('max', None),
            "Total Return": r.analyzers.returns.get_analysis().get('rtot', None)
        }

        return {"metrics": metrics}
    
    except Exception as e:
        return {"error": str(e)}