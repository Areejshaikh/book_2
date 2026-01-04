from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from .chapter import TextbookChapter


class ContentVersion(SQLModel, table=True):
    __tablename__ = "content_versions"

    id: int = Field(primary_key=True, index=True)
    chapter_id: int = Field(foreign_key="textbook_chapters.id", nullable=False)
    version: str = Field(max_length=20, nullable=False)
    content_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)