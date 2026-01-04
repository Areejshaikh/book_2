from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from ...services.rag_service import RAGService
from ...api.errors import ExternalKnowledgeError, InvalidQueryError
from ...middleware.rate_limit import check_rate_limit

router = APIRouter()

# 1. Request model updated to handle optional fields from frontend
class ChatRequest(BaseModel):
    query: str
    book_id: str
    session_id: str
    selected_text: Optional[str] = None
    user_id: Optional[str] = None

# 2. Response model
class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    retrieved_context: List[dict]
    confidence_level: str
    timestamp: str

# Initialize RAG service
rag_service = RAGService()

# 3. Corrected Route from "/docs" to "/chat"
@router.post("/chat", response_model=ChatResponse)
async def rag_chat_endpoint(request: ChatRequest, req: Request):
    """
    Production-ready RAG Chat API endpoint.
    """
    # Check rate limit
    check_rate_limit(req)

    try:
        # Validate input parameters
        if not request.query or len(request.query.strip()) == 0:
            raise InvalidQueryError("Query cannot be empty")

        # Process the query using RAG service
        # Humne 'selected_text' ko bhi pass kiya hai agar frontend se aaye
        result = rag_service.get_answer(
            query=request.query,
            book_id=request.book_id,
            session_id=request.session_id,
            selected_text=request.selected_text
        )

        # Add timestamp to the response
        result["timestamp"] = datetime.utcnow().isoformat()

        return ChatResponse(**result)

    except InvalidQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalKnowledgeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )