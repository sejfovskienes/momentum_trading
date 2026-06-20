from apscheduler.schedulers.background import BackgroundScheduler

from strategy import run_daily_strategy, run_weekly_rebalance
from utils import app_level_print

scheduler = BackgroundScheduler(timezone="US/Eastern")


def start_scheduler():
    app_level_print("Starting scheduler...")
    scheduler.add_job(
        run_daily_strategy,
        "cron",
        day_of_week="tue-fri",
        hour=16,
        minute=5,
        id="daily_strategy",
    )

    scheduler.add_job(
        run_weekly_rebalance,
        "cron",
        day_of_week="mon",
        hour=16,
        minute=10,
        id="weekly_rebalance",
    )

    scheduler.start()
