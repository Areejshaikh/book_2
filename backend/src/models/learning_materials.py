from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class LearningMaterials(SQLModel, table=True):
    __tablename__ = "learning_materials"

    id: int = Field(primary_key=True, index=True)
    chapter_id: int = Field(nullable=False)  # This would be a foreign key in a real implementation
    title: str = Field(max_length=500, nullable=False)
    content: str = Field(nullable=False)
    material_type: str = Field(max_length=100, default="general")  # quiz, summary, example, etc.
    difficulty_level: str = Field(max_length=50, default="intermediate")  # beginner, intermediate, advanced
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: int = Field(default=1)  # Using Integer as boolean (0 or 1)


class LearningMaterialsResponse(BaseModel):
    id: int
    chapter_id: int
    title: str
    content: str
    material_type: str
    difficulty_level: str
    created_at: datetime
    updated_at: datetime
    is_active: int

    class Config:
        from_attributes = True