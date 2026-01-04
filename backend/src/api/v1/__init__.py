"""
API v1 package initialization
"""
from fastapi import APIRouter
from . import chat, chat_endpoint, health, search, books, rag

# Create the main API v1 router
router = APIRouter()

# Include sub-routers
router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(chat_endpoint.router, tags=["Chat"])  # Main chat endpoint at /api/v1/chat
router.include_router(search.router, prefix="/search", tags=["Search"])
router.include_router(books.router, prefix="/books", tags=["Books"])
router.include_router(rag.router, prefix="/rag", tags=["RAG"])

__all__ = ["router"]