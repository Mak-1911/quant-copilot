from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import generate, backtest, explain, plot

app = FastAPI()
app.include_router(generate.router)
app.include_router(backtest.router)
app.include_router(explain.router)
app.include_router(plot.router)

@app.get("/")
def home():
    return {"status": "Quant Copilot running!"}
