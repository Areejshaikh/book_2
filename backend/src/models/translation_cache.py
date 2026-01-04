from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TranslationCache(SQLModel, table=True):
    __tablename__ = "translation_cache"

    id: int = Field(primary_key=True, index=True)
    source_content_hash: str = Field(max_length=255, nullable=False, index=True)
    source_language: str = Field(max_length=10, default="en")
    target_language: str = Field(max_length=10, nullable=False)
    translated_content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(nullable=False)