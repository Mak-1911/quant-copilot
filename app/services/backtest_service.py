import backtrader as bt
import yfinance as yf
import numpy as np
import pandas as pd
from app.utility.validators import validate_strategy_code
from app.models.strategy import Strategy
from app.db import get_session
from sqlmodel import select, Session

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
    


# ... existing code ...
# ... existing code ...
async def get_strategy_returns(strategy_id: int, session: Session, ticker: str = "AAPL") -> pd.Series:
    """
    Get returns data for a specific strategy
    
    Args:
        strategy_id: ID of the strategy to analyze
        session: Database session
        
    Returns:
        pd.Series: Daily returns for the strategy
    """
    try:
        print(f"[DEBUG] Starting get_strategy_returns with strategy_id={strategy_id}, ticker={ticker}")
        # Get strategy from database using provided session
        statement = select(Strategy).where(Strategy.id == strategy_id)
        strategy = session.exec(statement).first()
        
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        print(f"[DEBUG] Found strategy with ID {strategy_id}")
        print(f"[DEBUG] Strategy code length: {len(strategy.code) if strategy.code else 0}")
        print(f"[DEBUG] Strategy code preview: {strategy.code[:100] if strategy.code else 'None'}")
            
        # Execute strategy code
        local_vars = {}
        print(f"[DEBUG] Executing strategy code")
        exec(strategy.code, globals(), local_vars)
        strategy_class = next(
            (v for v in local_vars.values() 
             if isinstance(v, type) and issubclass(v, bt.Strategy)),
            None
        )
        
        if not strategy_class:
            raise ValueError("No valid Strategy class found")
        
        print(f"[DEBUG] Found strategy class: {strategy_class}")
        
        # Get historical data
        print(f"[DEBUG] Downloading data for ticker: {ticker}")
        df = yf.download(ticker, period="1y")
        print(f"Ticker type: {type(ticker)}, value: {ticker}")
        if df.empty:
            raise ValueError(f"No data for ticker: {ticker}")
        print(f"[DEBUG] Downloaded {len(df)} rows of data")
        
        # Fix column names if they are tuples (MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            print("[DEBUG] Converting MultiIndex columns to single index")
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Ensure column names are strings and lowercase
        df.columns = [str(col).lower() for col in df.columns]
        print(f"[DEBUG] Final column names: {list(df.columns)}")
        
        data = bt.feeds.PandasData(dataname=df)
        
        # Setup and run backtest
        print(f"[DEBUG] Setting up cerebro")
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(100000)
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class)
        # Add both analyzers to have options
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        print(f"[DEBUG] Running backtest")
        try:
            results = cerebro.run()
            print(f"[DEBUG] Backtest completed with {len(results)} results")
        except Exception as run_error:
            print(f"[ERROR] Error during cerebro.run(): {type(run_error).__name__}: {run_error}")
            # Try to get more details about the error
            import traceback
            traceback.print_exc()
            raise run_error
        
        # Try to extract daily returns from TimeReturn analyzer first
        try:
            print(f"[DEBUG] Extracting from TimeReturn analyzer")
            returns_dict = results[0].analyzers.timereturn.get_analysis()
            print(f"TimeReturn analyzer data type: {type(returns_dict)}")
            print(f"TimeReturn analyzer data: {returns_dict}")
            # Check if we got a dict and it's not empty
            if isinstance(returns_dict, dict) and len(returns_dict) > 0:
                returns = pd.Series(returns_dict)
                print(f"Successfully created returns series with {len(returns)} values")
                return returns
        except Exception as e:
            print(f"Failed to get returns from TimeReturn analyzer: {e}")
        
        # Fallback: try to get returns from the Returns analyzer
        try:
            print(f"[DEBUG] Extracting from Returns analyzer")
            # Get the total return and distribute it evenly across the period
            returns_analyzer = results[0].analyzers.returns.get_analysis()
            print(f"Returns analyzer data type: {type(returns_analyzer)}")
            print(f"Returns analyzer data: {returns_analyzer}")
            total_return = returns_analyzer.get('rtot', 0)
            # Handle case where rtot might be a tuple
            if isinstance(total_return, tuple):
                total_return = total_return[0] if len(total_return) > 0 else 0
            # Create a series with equal returns for each day
            num_days = len(df) if df is not None else 1
            if num_days > 0:
                # Calculate daily return that would result in the total return
                daily_return = (1 + total_return) ** (1/num_days) - 1
                returns = pd.Series([daily_return] * num_days)
                print(f"Created fallback returns series with {len(returns)} values")
                return returns
        except Exception as e:
            print(f"Failed to get returns from Returns analyzer: {e}")
        
        # Last resort: create a zero return series
        print("Using last resort zero return series")
        returns = pd.Series([0.0] * max(len(df), 1))
        return returns
            
    except Exception as e:
        # More defensive error handling to prevent the 'tuple' object error
        error_msg = str(e) if isinstance(e, (str, int, float)) else repr(e)
        print(f"[ERROR] Exception in get_strategy_returns: {error_msg}")
        raise ValueError(f"Error calculating returns: {error_msg}")
# ... existing code ...