from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.services.leaderboard_service import query_leaderboard
import logging

logger = logging.getLogger("scheduler")

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    def daily_job():
        logger.info("Running daily leaderboard job at %s", datetime.utcnow())
        top_daily = query_leaderboard(period="daily", limit=100)
        logger.info("Top daily leaderboard: %s", len(top_daily))

    scheduler.add_job(daily_job, "cron", hour=0, minute=5)
    scheduler.start()

    @app.on_event("shutdown")
    def _():
        scheduler.shutdown()
