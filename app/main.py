from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import generate, backtest, explain, plot, strategy, export, auth_otp, builder, leaderboard, metrics
from app.scheduler import start_scheduler
from app.db import init_db
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(leaderboard.router)
app.include_router(metrics.router)
start_scheduler(app)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Quant Copilot running!"}
