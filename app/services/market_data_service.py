import yfinance as yf
from typing import Optional, Dict
from datetime import datetime
import pandas as pd

class MarketDataService:
    """Service for fetching real time and historical market data"""
    @staticmethod
    def get_current_price(symbol:str) -> Optional[float]:
        """Get latest price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                data = ticker.history(period="5d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        except Exception as e:
            print(f"Error checking market status: {e}")
            return False

    @staticmethod
    def get_intraday_data(symbol:str, interval: str="1m") -> Optional[pd.DataFrame]:
        """Get intraday data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval=interval)
            return data if not data.empty else None
        except Exception as e:
            print(f"Error fetching intraday data for {symbol}: {e}")
            return None

    @staticmethod
    def is_market_open(symbol:str) -> bool:
        """Check if the market if currently open for the symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            #For US Markets
            if 'exchange' in info:
                exchange = info['exchange'].upper()
                #Simple Check - Enhance with actual market hours
                now = datetime.now()
                return True
        except Exception as e:
            print(f"Error checking market status: {e}")
            return False

            