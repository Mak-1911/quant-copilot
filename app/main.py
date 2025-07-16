from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Quant Copilot running!"}
