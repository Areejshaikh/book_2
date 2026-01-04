from sqlmodel import SQLModel, Field
from typing import Optional


class TextbookChapter(SQLModel, table=True):
    __tablename__ = "textbook_chapters"

    id: int = Field(primary_key=True, index=True)
    title: str = Field(max_length=500, nullable=False)
    slug: str = Field(unique=True, max_length=500, nullable=False, index=True)
    content: str = Field(nullable=False)
    version: str = Field(default='1.0.0', max_length=20)
    position: int = Field(unique=True, nullable=False)
    word_count: int = Field(default=0)
    estimated_reading_time: int = Field(default=0)  # in minutes
    chapter_metadata: Optional[str] = Field(default=None)  # JSON string for additional metadata