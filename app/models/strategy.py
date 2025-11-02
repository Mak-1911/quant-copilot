from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime

class Strategy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    prompt:str
    code:str
    user_id: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)