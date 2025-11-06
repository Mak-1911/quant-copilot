from appscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlmodel import Session, select
from app.models.paper_trading import PaperOrder, OrderStatus
from app.services.paper_trading_service import PaperTradingService
from app.services.market_data_service import MarketDataService
from app.db import get_session
import logging

logger = logging.getLogger("paper_trading_executor")

class PaperTradingExecutor:
    """Engine that executes paper trading orders during market hours"""

    def __init__(self):
        self.scheduler = None

    def start(self):
        """Start the execution engine"""
        self.scheduler = BackgroundScheduler()
    
        #Run every minute during market hours
        #For production, you'd want more sophisticated market hours detection
        self.scheduler.add_job(
            self.process_pending_orders,
            "interval",
            minutes=1,
            id="process_paper_orders",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Paper trading executor started")

    def stop(self):
        """Stop the execution enginer"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Paper trading Executor stopped")
    
    def process_pending_orders(self):
        """Process all pending orders"""
        try:
            with get_session() as session:
                #Get all pending orders
                pending_orders = session.exec(
                    select(PaperOrder).where(
                        PaperOrder.status == OrderStatus.PENDING
                    )
                ).all()
                logger.info(f"Processing {len(pending_orders)} pending orders")
                
                for order in pending_orders:
                    try:
                        #Try to execute the orders
                        PaperTradingService.execute_order(order.id, session)
                    except Exception as e:
                        logger.error(f"Error executing order {order.id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in process_pending_orders: {e}")
    
    def update_positions(self):
        """Update position prices and account balances"""
        try:
            with get_session as session:
                from app.models.paper_trading import PaperTradingAccount, PaperPosition
                accounts = session.exec(select(PaperTradingAccount)).all()

                for account in accounts:
                    PaperTradingService._update_account_balance(account, session)
                    session.commit()
        
        except Exception as e:
            logger.error(f"Error updating positions: {e}")


#GLobal executor instance
_executor = None

def get_executor() -> PaperTradingExecutor:
    global _executor
    if _executor is None:
        _executor = PaperTradingExecutor()
    return _executor