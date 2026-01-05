import uuid
from datetime import datetime
from typing import Optional
from ..services.qdrant_service import qdrant_manager
from ..services.llm_service import LLMService

class RAGService:
    def __init__(self):
        self.qdrant_service = qdrant_manager
        self.llm_service = LLMService()

    def get_answer(self, query: str, bookId: str, session_id: str, selected_text: Optional[str] = None) -> dict:
        msg_id = str(uuid.uuid4())
        
        # 1. Context Retrieval
        if selected_text:
            retrieved_contexts = self.qdrant_service.bypass_retrieval_for_selected_text(
                selected_text=selected_text, 
                book_id=bookId
            )
        else:
            retrieved_contexts = self.qdrant_service.search_relevant_chunks(
                query=query, 
                book_id=bookId, 
                top_k=5
            )

        # 2. Check if context exists
        if not retrieved_contexts:
            return {
                "response": "Maaf kijiye, is bare mein textbook mein malomat nahi mili.",
                "confidence_level": "Low",
                "session_id": session_id,
                "message_id": msg_id,
                "retrieved_context": [],
                "timestamp": datetime.now().isoformat()
            }

        # 3. Generate Answer
        context_str = "\n".join([ctx.chunk_text for ctx in retrieved_contexts])
        answer = self.llm_service.generate_response(query, context_str)

        return {
            "response": answer,
            "confidence_level": "High",
            "session_id": session_id,
            "message_id": msg_id,
            "retrieved_context": [
                {
                    "context_id": c.context_id,
                    "chunk_text": c.chunk_text,
                    "similarity_score": c.similarity_score,
                    "book_id": bookId,
                    "embedding_id": c.context_id
                } for c in retrieved_contexts
            ],
            "timestamp": datetime.now().isoformat()
        }