from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"

    id: int = Field(primary_key=True, index=True)
    user_id: int = Field(index=True, nullable=False)
    chapter_id: int = Field(index=True, nullable=False)
    progress: float = Field(nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow)