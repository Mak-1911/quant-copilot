from sqlmodel import SQLModel, create_engine, Session
import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)
def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)