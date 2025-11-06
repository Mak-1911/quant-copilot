from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.paper_trading import (
    PaperTradingAccount, PaperOrder, PaperTrade, PaperPosition,
    OrderSide, OrderType, OrderStatus
)
from app.services.market_data_service import MarketDataService
from app.models.strategy import Strategy
import logging

logger = logging.getLogger("paper_trading")

class PaperTradingService:
    @staticmethod
    def get_or_create_account(user_id: int, initial_capital:float=100000.0, session:Session=None) -> PaperTradingAccount:
        """Get existing accountn or create new one for user"""
        if session is None:
            from app.db import get_session
            session = next(get_session())

        account = session.exec(
            select(PaperTradingAccount).where(
                PaperTradingAccount.user_id == user_id,
                PaperTradingAccount.is_active == True
            )
        ).first()

        if not account:
            account = PaperTradingAccount(
                user_id = user_id,
                initial_capital = initial_capital,
                current_balance = current_balance,
                available_cash = initial_capital
            )
            session.add(account)
            session.commit()
            session.refresh(account)

        return account


    @staticmethod
    def create_order(
        account_id: str,
        symbol: str,
        side: OrderSide, 
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        strategy_id: Optional[int] = None,
        session: Session = None
    ) -> PaperOrder:
        """Create a new paper trading order"""
        if session is None:
            from app.db import get_session
            session = next(get_session())

        #Validate Order
        if quantity <= 0:
            raise ValueError("Quantity Must be Positive")
        
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and price is None:
            raise ValueError(f"Price required for {order_type}")
        
        if order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and stop_price is None:
            raise ValueError(f"Stop Price required for {order_type}")
        
        #get account 
        account = session.get(PaperTradingAccount, account_id)
        if not account:
            raise ValueError(f"Account not Found!")
        
        #For Market Orders, getting current price
        if order_type == OrderType.MARKET:
            current_price = MarketDataService.get_current_price(symbol)
            if current_price is None:
                raise ValueError(f"Unable to get current price for {symbol}")
            price = current_price

        #Check available cash for buy orders
        if side == OrderSide.BUY:
            required_cash = quantity * (price or 0)
            if account.available_cash < required_cash:
                raise ValueError(f"Insufficient cash. Required: ${required_cash:.2f}, Available: ${account.available_cash:.2f}")

        #Check position for sell orders
        if side == OrderSide.SELL:
            position = session.exec(
                select(PaperPosition).where(
                    PaperPosition.account_id == account_id,
                    PaperPosition.symbol == symbol
                )
            ).first()

            if not position or position.quantity < quantity:
                raise ValueError(f"Insufficient Position. Trying to sell {quantity},  but have {position.quantity if position else 0}")        
        
        #create order 
        order = PaperOrder(
            account_id = account_id,
            strategy_id = strategy_id,
            symbol = symbol,
            side = side,
            order_type = order_type,
            quantity = quantity,
            price = price,
            stop_price = stop_price,
            status = OrderStatus.PENDING
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        #Trying to execute the order immediately for market orders
        if order_type == OrderType.MARKET:
            PaperTradingService.execute_order(order.id, session)

        return order

    @staticmethod
    def execute_order(order_id: int, session:Session=None) -> Optional[PaperTrade]:
        """Execute a pending order if conditions are met"""
        if session is None:
            from app.db import get_session
            session = next(get_session())

        order = session.get(PaperTrade, order_id)
        if not order or order.status != OrderStatus.PENDING:
            return None

        current_price = MarketDataService.get_current_price(order.symbol)
        if current_price is None:
            logger.warning(f"Could not get price for {order.symbol}, order {order_id} remains pending!")
            return None
        
        #Lets check if order can be executed based on type
        fill_price = None
        if order.order_type == OrderType.MARKET:
            fill_price = current_price
        elif order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and current_price <= order.price:
                fill_price = order.price
            elif order.side == OrderSide.SELL and current_price >= order.price:
                fill_price = order.price

        elif order.order_type == OrderType.STOP:
            if order.side == OrderSide.BUY and current_price >= order.stop_price:
                fill_price = current_price
            elif order.side == OrderSide.SELL and current_price <= order.stop_price:
                fille_price = current_price
        
        elif order.order_type == OrderType.STOP_LIMIT:
            if order.side == OrderSide.BUY:
                if current_price >= order.stop_price and current_price <= order.price:
                    fill_price = order.price
            elif order.side == OrderSide.SELL:
                if current_price <= order.stop_price and current_price >= order.price:
                    fill_price = order.price

        if fill_price is None:
            return None

        #Execute the trade
        return PaperTradingService._execute_trade(order, fill_price, session)

    @staticmethod
    def _execute_trade(order: PaperOrder, fill_price: float, session: Session) -> PaperTrade:
        """Executing trade from an order"""
        account = session.get(PaperTradingAccount, order.account_id)
        if not account:
            raise ValueError("Account Not Found")

        #creating trade record
        trade = PaperTrade(
            account_id=order.account_id,
            order_id=order.id,
            strategy_id=order.strategy_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            timestamp=datetime.utcnow()
        )

        #Update Order
        order.filled_quantity = order.quantity
        order.average_fill_price = fill_price
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.utcnow()

        #updating cash
        if order.side == OrderSide.BUY:
            cost = order.quantity * fill_price
            account.available_cash -= cost
        else: #SELL
            proceeds = order.quantity * fill_price 
            account.available_cash += proceeds

        #Update Postion
        PaperTradingService._update_position(
            account.id,
            order.symbol,
            order.quantity if order.side == OrderSide.BUY else -order.quantity,
            fill_price, 
            session
        )          

        #update account balance
        PaperTradingService._update_account_balance(account, session)
        session.add(trade)
        session.add(order)
        session.add(account)
        session.commit()
        session.refresh(trade)
        logger.info(f"Executed trade: {order.side} {order.quantity} {order.symbol} @ ${fill_price:.2f}")
        return trade

    
    @staticmethod 
    def _update_positon(
        account_id: int,
        symbol: str,
        quantity_change: float,
        price: float,
        session: Session
    ):
        """Update or create position"""
        position = session.exec(
            select(PaperPosition).where(
                PaperPosition.account_id == account_id,
                PaperPosition.symbol == symbol
            )
        ).first()

        if postion:
            #update existing position
            total_cost = (position.quantity * position.avg_entry_price ) + (quantity_change*price)
            new_quantity = position.quantity + quantity_change

            if abs(new_quantity) < 0.0001: #positon close
                #Calculating realsied pnl
                if position.quantity > 0 and quantity_change<0: #Long closing
                    position.realized_pnl += (price - position.avg_entry_price) * abs(quantity_change)
                elif position.quantity < 0 and quantity_change > 0: #Short Covering
                    position.realized_pnl += (postion.avg_entry_price - price) * abs(quantity_change)
                
                session.delete(position)
            else:
                position.quantity = new_quantity
                position.avg_entry_price = total_cost / new_quantity if new_quantity != 0 else price
                position.updated_at = datetime.utcnow()

        else:
            #Creating new position
            position = PaperPosition(
                account_id = account_id,
                symbol = symbol,
                quantity = quantity_change,
                avg_entry_price = price,
                current_price = price
            )
            session.add(position)
    
    @staticmethod
    def _update_account_balance(account: PaperTradingAccount, session: Session):
        """Update account balance including unrealized PnL"""
        #Get all Positions
        positions = session.exec(
            select(PaperPosition).where(PaperPosition.account_id == account.id)
        ).all()

        unrealized_pnl = 0.0
        for position in positions:
            current_price = MarketDataService.get_current_price(position.symbol) or position.current_price
            position.current_price = current_price

            if position.quantity > 0: #Long position
                position.unrealized_pnl = (current_price - position_avg_entry_price) * position.quantity
            else: #Short positon
                position.unrealized_pnl = (position.avg_entry_price - current_price) * abs(position.quantity)
            
            unrealized_pnl += position.unrealized_pnl
            position.updated_at = datetime.utcnow()
        
        #Total balance = cash + market value of positions
        account.current_balance = account.available_cash + sum(
            (p.quantity * p.current_price) + p.realized_pnl
            for p in positions
        )
        account.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_portfolio(account_id:int, session:Session = None) -> Dict[str, Any]:
        """Get complete portfolio information"""
        if session is None:
            from app.db import get_session
            session = next(get_session())

        account = session.get(PaperTradingAccount, account_id)
        if not account:
            raise ValueError("Account Not Found!")
        
        #Update balance first 
        PaperTradingService._update_account_balance(account, session)

        positions = session.exec(
            select(PaperPosition).where(PaperPosition.account_id == account_id)
        ).all()

        orders = session.exec(
            select(PaperOrder).where(
                PaperOrder.account_id == account_id,
            ).order_by(PaperOrder.created_at.desc())
        ).limit(50).all()

        trades = session.exec(
            select(PaperTrade).where(
                PaperTrade.account_id == account_id
            ).order_by(PaperTrade.timestamp.desc())
        ).limit(100).all()

        return {
            "account":{
                "id":account.id,
                "initial_capital": account.initial_capital,
                "current_balance": account.current_balance,
                "available_cash": account.available_cash,
                "total_pnl" : account.current_balance - account.initial_capital,
                "total_return_pct": ((account.current_balance - account.initial_capital) / account.initial_capital) * 100
            },
            "positions": [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "avg_entry_price": p.avg_entry_price,
                    "current_price": p.current_price,
                    "unrealized_pnl": p.unrealized_pnl,
                    "realized_pnl": p.realized_pnl,
                    "market_value": p.quantity * p.current_price
                }
                for p in positions
            ],
            "recent_orders":[
                {
                    "id":o.id,
                    "symbol": o.symbol,
                    "side": o.side,
                    "order_type": o.order_type,
                    "quantity": o.quantity,
                    "status": o.status,
                    "created_at": o.created_at.isoformat()
                }
                for o in orders
            ],
            "recent_trades": [
                {
                    "id": t.id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in trades
            ]
        }

    @staticmethod
    def cancel_order(order_id: int, session: Session = None) -> bool:
        """Cancel a pending order"""
        if session is None:
            from app.db import get_session
            session = next(get_session())
        
        order = session.get(PaperOrder, order_id)
        if not order:
            return False

        if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
            return False

        order.status = OrderStatus.CANCELLED
        session.add(order)
        session.commit()
        return True