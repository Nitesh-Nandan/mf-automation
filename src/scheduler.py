#!/usr/bin/env python3
"""
Simple Scheduler for MF Dip Analysis
Spring-like @Scheduled decorator approach
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

sys.path.insert(0, str(Path(__file__).parent))
from main import run_analysis_and_send_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()


# Choose one schedule (uncomment the one you want):


# Every minute (for testing)
@scheduler.scheduled_job(IntervalTrigger(minutes=1))
def run_every_minute():
    """@Scheduled(fixedRate = 60000)"""
    logger.info("Running MF analysis...")
    try:
        run_analysis_and_send_email(mode="conservative")
        logger.info("✅ Completed")
    except Exception as e:
        logger.error(f"❌ Failed: {e}")


# Every 5 minutes
# @scheduler.scheduled_job(IntervalTrigger(minutes=5))
# def run_every_5_minutes():
#     """@Scheduled(fixedRate = 300000)"""
#     logger.info("Running MF analysis...")
#     try:
#         run_analysis_and_send_email(mode='conservative')
#         logger.info("✅ Completed")
#     except Exception as e:
#         logger.error(f"❌ Failed: {e}")


# Daily at 9 AM
# @scheduler.scheduled_job(CronTrigger(hour=9, minute=0))
# def run_daily_at_9am():
#     """@Scheduled(cron = "0 0 9 * * ?")"""
#     logger.info("Running MF analysis...")
#     try:
#         run_analysis_and_send_email(mode='conservative')
#         logger.info("✅ Completed")
#     except Exception as e:
#         logger.error(f"❌ Failed: {e}")


# Weekly on Monday at 9 AM
# @scheduler.scheduled_job(CronTrigger(day_of_week='mon', hour=9, minute=0))
# def run_weekly_monday():
#     """@Scheduled(cron = "0 0 9 ? * MON")"""
#     logger.info("Running MF analysis...")
#     try:
#         run_analysis_and_send_email(mode='conservative')
#         logger.info("✅ Completed")
#     except Exception as e:
#         logger.error(f"❌ Failed: {e}")


if __name__ == "__main__":
    logger.info("Scheduler started - Press Ctrl+C to stop")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
        scheduler.shutdown()
