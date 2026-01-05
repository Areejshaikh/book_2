from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from uuid import UUID
from ...models.user_query import UserQueryCreate
from ...services.rag_service import RAGService

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    session_id: str,
    bookId: str,
    query: str,
    selected_text: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Initiate a conversation or continue an existing one with the RAG chatbot.

    Request Body:
    {
      "session_id": "uuid",
      "book_id": "uuid",
      "query": "string (the user's question)",
      "selected_text": "string (optional, text the user highlighted)",
      "user_id": "uuid (optional)"
    }

    Response (200 OK):
    {
      "response_id": "uuid",
      "session_id": "uuid",
      "query": "string (echo of the user's question)",
      "answer": "string (the chatbot's response)",
      "confidence_level": "enum (high|medium|low)",
      "source_chunks_used": ["uuid"],
      "grounded_in_content": "boolean",
      "timestamp": "datetime"
    }
    """
    try:
        # Generate response using RAG service
        rag_service = RAGService()
        response = rag_service.get_answer(
            query=query,
            book_id=bookId,
            session_id=session_id,
            selected_text=selected_text
        )

        # Store the conversation turn in history
        store_conversation_turn(
            session_id=session_id,
            query=query,
            answer=response["response"],
            confidence_level=response["confidence_level"],
            timestamp="2025-12-31T12:00:00Z"  # Using a placeholder timestamp since RAG service doesn't return one
        )

        # Format response to match expected API structure
        formatted_response = {
            "response_id": response["message_id"],
            "session_id": response["session_id"],
            "query": query,
            "answer": response["response"],
            "confidence_level": response["confidence_level"],
            "source_chunks_used": [ctx["chunk_id"] for ctx in response["retrieved_context"]],
            "grounded_in_content": len(response["retrieved_context"]) > 0,
            "timestamp": "2025-12-31T12:00:00Z"  # Using a placeholder
        }

        return formatted_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

# In-memory storage for conversation history (in a real implementation, this would be in a database)
conversation_history = {}

@router.get("/chat/{session_id}/history")
async def get_conversation_history(session_id: str):
    """
    Retrieve the conversation history for a specific session.

    Path Parameters:
    - session_id: UUID of the session

    Response (200 OK):
    {
      "session_id": "uuid",
      "history": [
        {
          "query": "string",
          "answer": "string",
          "timestamp": "datetime",
          "confidence_level": "enum (high|medium|low)"
        }
      ]
    }
    """
    # In a real implementation, this would retrieve the conversation history
    # from a database. For now, we'll use in-memory storage.
    history = conversation_history.get(session_id, [])
    return {
        "session_id": session_id,
        "history": history
    }

# Internal function to store conversation history
def store_conversation_turn(session_id: str, query: str, answer: str, confidence_level: str, timestamp: str):
    """Store a conversation turn in the history"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append({
        "query": query,
        "answer": answer,
        "timestamp": timestamp,
        "confidence_level": confidence_level
    })