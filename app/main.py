from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import generate, backtest

app = FastAPI()
app.include_router(generate.router)
app.include_router(backtest.router)

@app.get("/")
def home():
    return {"status": "Quant Copilot running!"}
