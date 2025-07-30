from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import generate, backtest, explain, plot, strategy, export, auth_otp, builder
from app.db import init_db

app = FastAPI()
init_db()
app.include_router(generate.router)
app.include_router(backtest.router)
app.include_router(explain.router)
app.include_router(plot.router)
app.include_router(strategy.router)
app.include_router(export.router)
app.include_router(auth_otp.router)
app.include_router(builder.router)
@app.get("/")
def home():
    return {"status": "Quant Copilot running!"}
