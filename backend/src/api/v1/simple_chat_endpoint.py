"""
Simple RAG Chat API endpoint that returns response in the exact format expected by the frontend
POST /api/v1/chat with the exact JSON schema required by the frontend
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from ...services.rag_service import RAGService
from ...api.errors import ExternalKnowledgeError, InvalidQueryError
from ...middleware.rate_limit import check_rate_limit


router = APIRouter()

# Request model matching what might be expected by the frontend
class SimpleChatRequest(BaseModel):
    query: str
    book_id: Optional[str] = "default_book"  # Default value to maintain compatibility
    session_id: Optional[str] = None


# Response model matching the exact format expected by the frontend
class SimpleChatResponse(BaseModel):
    response: str
    sources: List[dict]


# Initialize RAG service
rag_service = RAGService()


@router.post("/")  # This will be mounted at /api/v1/chat to match frontend expectation
async def simple_chat_endpoint(request: SimpleChatRequest, req: Request):
    """
    Simple RAG Chat API endpoint that returns response in the exact format expected by the frontend.

    Request JSON Schema:
    {
      "query": "string",
      "book_id": "string" (optional),
      "session_id": "string" (optional)
    }

    Response JSON Schema (as expected by frontend):
    {
      "response": "string",
      "sources": []
    }
    """
    # Check rate limit
    check_rate_limit(req)

    try:
        # Validate input parameters
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Generate a session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Process the query using RAG service
        result = rag_service.get_answer(
            query=request.query,
            book_id=request.bookId,
            session_id=session_id
        )

        # Extract the response and format sources as expected by the frontend
        response_text = result.get("response", "")
        
        # Format sources from retrieved_context
        sources = []
        retrieved_context = result.get("retrieved_context", [])
        for context in retrieved_context:
            sources.append({
                "id": context.get("chunk_id", ""),
                "text": context.get("text", ""),
                "similarity_score": context.get("similarity_score", 0.0),
                "source_url": context.get("source_url", "")  # If available in context
            })

        # Return response in the exact format expected by the frontend
        return SimpleChatResponse(
            response=response_text,
            sources=sources
        )

    except InvalidQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalKnowledgeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        # Re-raise FastAPI HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )