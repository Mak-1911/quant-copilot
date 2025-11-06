from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class PaperTradingAccount(SQLModel, table=True):
    __tablename__ = "paper_trading_accounts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    initial_capital: float = Field(default=100000.0)
    current_balance: float = Field(default=100000.0)
    available_cash: float = Field(default=100000.0)
    is_active: bool = Field(default=True)
    created_at: bool = Field(default_factory=datetime.utcnow)
    updated_at: bool = Field(default_factory=datetime.utcnow)

class PaperOrder(SQLModel, table=True):
    __tablename__ = "paper_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="paper_trading_accounts.id", index=True)
    strategy_id: Optional[int] = Field(default=None, foreign_key="strategy.id", index=True)
    symbol : str = Field(index = True)
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime = Field(default_factory = datetime.utcnow, index=True)

class PaperTrade(SQLModel, table=True):
    __tablename___ = "paper_trades"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="paper_trading_accounts.id", index=True)
    order_id : int = Field(foreign_key="paper_orders.id", index=True)
    strategy_id: Optional[int] = Field(default=None, foreign_key="strategy.id", index=True)
    symbol: str = Field(index=True)
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

class PaperPosition(SQLModel, table=True):
    __tablename___ = "paper_positions"
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="paper_trading_accounts.id", index=True)
    symbol: str = Field(index=True)
    quantity: float
    avg_entry_price: float
    current_price: float = Field(default=0.0)
    unrealized_pnl: float = Field(default=0.0)
    realized_pnl: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    