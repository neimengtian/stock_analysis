from fastapi import FastAPI
from .routes import stocks, ml

app = FastAPI(
    title="Stock Analysis API",
    description="Stock data fetching, ML training, and prediction endpoints",
    version="0.1.0",
)

app.include_router(stocks.router)
app.include_router(ml.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
