import logging
from datetime import datetime, time
from threading import Thread, Event
from .data_tasks import fetch_multiple_stocks_task
from .ml_tasks import train_model_task

logger = logging.getLogger(__name__)

DEFAULT_TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]


class TaskScheduler:
    def __init__(self, tickers: list[str] = None):
        self.tickers = tickers or DEFAULT_TICKERS
        self._stop_event = Event()
        self._thread = None

    def run_daily_fetch(self):
        logger.info("Running daily data fetch")
        fetch_multiple_stocks_task(self.tickers)

    def run_daily_retrain(self):
        logger.info("Running daily model retraining")
        for ticker in self.tickers:
            train_model_task(ticker)

    def start(self, fetch_hour: int = 18, retrain_hour: int = 19):
        def _loop():
            while not self._stop_event.is_set():
                now = datetime.now()
                if now.hour == fetch_hour and now.minute == 0:
                    self.run_daily_fetch()
                if now.hour == retrain_hour and now.minute == 0:
                    self.run_daily_retrain()
                self._stop_event.wait(60)

        self._thread = Thread(target=_loop, daemon=True)
        self._thread.start()
        logger.info(f"Scheduler started: fetch at {fetch_hour}:00, retrain at {retrain_hour}:00")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
