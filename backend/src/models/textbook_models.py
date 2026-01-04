from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from .user import User  # Assuming there's a user model


class TextbookBase(SQLModel):
    title: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)  # Entire textbook content
    is_published: bool = Field(default=False)


class Textbook(TextbookBase, table=True):
    __tablename__ = "textbooks"

    id: int = Field(primary_key=True, index=True)
    owner_id: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships - these would be defined in the User model as back_populates
    # owner: "User" = Relationship(back_populates="textbooks")
    # modules: List["LearningModule"] = Relationship(back_populates="textbook")


class TextbookResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningModule(SQLModel, table=True):
    __tablename__ = "learning_modules"

    id: int = Field(primary_key=True, index=True)
    title: str = Field(index=True, nullable=False)
    content: Optional[str] = Field(default=None)  # Detailed content of the learning module
    textbook_id: int = Field(foreign_key="textbooks.id", nullable=False)
    author_id: int = Field(foreign_key="users.id", nullable=False)
    position: int = Field(default=0)  # Order of the module in the textbook
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Context7Session(SQLModel, table=True):
    __tablename__ = "context7_sessions"

    id: int = Field(primary_key=True, index=True)
    session_id: str = Field(unique=True, nullable=False)  # Session ID from Context7
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    textbook_id: Optional[int] = Field(default=None, foreign_key="textbooks.id")
    context_data: Optional[str] = Field(default=None)  # JSON or serialized context data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)