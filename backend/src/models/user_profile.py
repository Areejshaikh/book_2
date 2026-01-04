from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    id: int = Field(primary_key=True, index=True)
    user_id: int = Field(nullable=False)  # This might be a foreign key in a real implementation
    name: Optional[str] = Field(max_length=255, default=None)
    bio: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(max_length=500, default=None)
    preferences: Optional[str] = Field(default=None)  # JSON string for user preferences
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)