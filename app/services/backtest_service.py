import backtrader as bt
import yfinance as yf

def calculate_cagr(initial_value, final_value, periods):
    return ((final_value / initial_value) ** (1 / periods)) - 1

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
