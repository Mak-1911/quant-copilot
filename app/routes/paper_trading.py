from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlmodel import Session
from app.db import get_session
from app.auth.utils import get_current_user
from app.models.users import User
from app.models.paper_trading import OrderSide, OrderType, PaperOrder
from app.services.paper_trading_service import PaperTradingService

router = APIRouter(prefix="/paper", tags=["Paper Trading"])

class CreateOrderRequest(BaseModel):
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    strategy_id: Optional[int] = None

class AccountResponse(BaseModel):
    id: int
    initial_capital: float
    current_balance: float
    available_cash: float
    total_pnl: float
    total_return_pct: float

@router.post("/account/create")
def create_account(
    initial_capital: float = Query(default=100000.0, ge=1000.0),
    current_user: User = Depends(get_current_user)
):
    """Create or get paper trading account"""
    with get_session() as session:
        account = PaperTradingService.get_or_create_account(
            user_id = current_user.id,
            initial_capital = initial_capital,
            session = session
        )
        return {
            "account_id": account.id,
            "initial_capital": account.initial_capital,
            "current_balance": account.current_balance,
            "available_cash": account.available_cash
        }

@router.get("/account")
def get_account(current_user: User = Depends(get_current_user)):
    """Get Users paper trading account"""
    with get_session() as session:
        account = PaperTradingService.get_or_create_account(
            user_id = current_user.id,
            session = session
        )
        return {
            "id": account.id,
            "initial_capital": account.initial_capital,
            "current_balance": account.current_balance,
            "available_cash": account.available_cash,
            "total_pnl": account.current_balance - account.initial_capital,
            "total_return_pct": ((account.current_balance - account.initial_capital)/account.initial_capital)
        }


@router.get("/portfolio")
def get_portfolio(current_user: User = Depends(get_current_user)):
    """Get Complete Portfolio information"""
    with get_session() as session:
        account = PaperTradingService.get_or_create_account(
            user_id = current_user.id,
            session = session
        )
        portfolio = PaperTradingService.get_portfolio(account.id, session)
        return portfolio

@router.post("/order")
def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new paper trading order"""
    try:
        with get_session() as session:
            account = PaperTradingService.get_or_create_account(
                user_id = current_user.id,
                session=session
            )
            order = PaperTradingService.create_order(
                account_id=account.id,
                symbol = request.symbol,
                side = request.side,
                order_type = request.order_type,
                quanity = request.quantity,
                price = request.price,
                stop_price = request.stop_price,
                strategy_id = request.strategy_id,
                session = session
            )
            return {
                "order_id": order.id,
                "status": order.status,
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "order_type": order.order_type
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
def get_orders(
    status: Optional[str] = Query(None),
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get User's orders"""
    with get_session() as session:
        from sqlmodel import select
        from app.models.paper_trading import PaperOrder, OrderStatus

        account = PaperTradingService.get_or_create_account(
            user_id = current_user.id,
            session=session
        )

        query = select(PaperOrder).where(PaperOrder.account_id == account.id)

        if status:
            try:
                order_status = OrderStatus(status.upper())
                query = query.where(PaperOrder.status == order_status)
            except ValueError:
                pass
        
        orders = session.exec(query.order_by(PaperOrder.created_at.desc()).limit()).all()
        return [
            {
                "id": o.id,
                "symbol": o.symbol,
                "side": o.side,
                "order_type": o.order_type,
                "quantity": o.quantity,
                "price": o.price,
                "filled_quantity": o.filled_quantity,
                "average_fill_price": o.average_fill_price,
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "filled_at": o.filled_at.isoformat() if o.filled_at else None
            }
            for o in orders
        ]

@router.delete("/order/{order_id}")
def cancel_order(order_id: int, current_user: User = Depends(get_current_user)):
    """Cancel a pending order"""
    with get_session() as session:
        from app.models.paper_trading import PaperOrder

        order = session.get(PaperOrder, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        account = PaperTradingService.get_or_create_account(
            user_id=current_user.id,
            session=session
        )

        if order.account_id != account.id:
            raise HTTPException(status_code=403, detail="Not your order")
        
        success = PapertradingService.cancel_order(order_id, session)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot cancel this order")
        
        return {"message": "Order Cancelled"}


@router.get("/trades")
def get_trades(
    symbol: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    current_user: User = Depends(get_current_user)
):
    """Get user's trade history"""
    with get_session() as session:
        from sqlmodel import select
        from app.model.paper_trading import PaperTrade

        account = PapertradingService.get_or_create_account(
            user_id=current_user.id,
            session=session
        )

        query = select(PaperTrade).where(PaperTrade.account_id == account.id)
        if symbol:
            query = query.where(PaperTrade.symbol == symbol)
        trades = session.exec(query.order_by(PaperTrade.timestamp.desc()).limit(limit)).all()

        return [
            {
                "id": t.id,
                "symbol": t.symbol,
                "side": t.side,
                "quantity": t.quantity,
                "price": t.price,
                "timestamp": t.timestamp.isoformat(),
                "strategy_id": t.strategy_id
            }
            for t in trades
        ]

@router.get("/positions")
def get_positions(current_user: User=Depends(get_current_user)):
    """Get user's current positions"""
    with get_session() as session:
        account = PaperTradingService.get_or_create_account(
            user_id=current_user.id,
            session=session
        )

        portfolio = PaperTradingService.get_portfolio(account.id, session)
        return portfolio