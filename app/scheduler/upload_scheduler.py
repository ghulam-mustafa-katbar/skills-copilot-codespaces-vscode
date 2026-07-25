"""APScheduler wrapper for automated upload cycles."""

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


class UploadScheduler:
    """Schedules recurring jobs for queue scan and upload."""

    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        self.scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")

    def schedule_interval(self, callback: callable, minutes: int) -> None:
        """Schedule callback every N minutes."""

        self.scheduler.add_job(callback, "interval", minutes=minutes, id="upload-interval", replace_existing=True)

    def schedule_cron(self, callback: callable, cron_expression: str) -> None:
        """Schedule callback using five-field cron expression."""

        minute, hour, day, month, day_of_week = cron_expression.split()
        self.scheduler.add_job(
            callback,
            "cron",
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            id="upload-cron",
            replace_existing=True,
        )
