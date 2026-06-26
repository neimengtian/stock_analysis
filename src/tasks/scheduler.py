from celery.schedules import crontab
from .celery_app import celery_app


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=18, minute=0),
        fetch_daily_data.s(),
        name="fetch-daily-data",
    )

    sender.add_periodic_task(
        crontab(hour=19, minute=0),
        retrain_models.s(),
        name="retrain-models",
    )


@celery_app.task(name="scheduler.fetch_daily_data")
def fetch_daily_data():
    from .data_tasks import fetch_multiple_stocks_task

    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    return fetch_multiple_stocks_task.delay(tickers)


@celery_app.task(name="scheduler.retrain_models")
def retrain_models():
    from .ml_tasks import train_model_task

    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    for ticker in tickers:
        train_model_task.delay(ticker)
