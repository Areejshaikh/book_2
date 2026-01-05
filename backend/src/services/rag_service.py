import uuid
import logging
from datetime import datetime
from typing import Optional
from ..services.qdrant_service import qdrant_manager
from ..services.llm_service import LLMService

# Logs enable karein taake Railway mein error dikhe
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.qdrant_service = qdrant_manager
        self.llm_service = LLMService()

    def get_answer(self, query: str, bookId: str, session_id: str, selected_text: Optional[str] = None) -> dict:
        msg_id = str(uuid.uuid4())
        
        try:
            # 1. Context Retrieval
            if selected_text:
                logger.info(f"Bypassing retrieval for selected text. BookID: {bookId}")
                retrieved_contexts = self.qdrant_service.bypass_retrieval_for_selected_text(
                    selected_text=selected_text, 
                    book_id=bookId
                )
            else:
                logger.info(f"Searching Qdrant for: {query} in BookID: {bookId}")
                retrieved_contexts = self.qdrant_service.search_relevant_chunks(
                    query=query, 
                    book_id=bookId, 
                    top_k=5
                )

            # 2. Check if context exists
            if not retrieved_contexts:
                logger.warning(f"No context found for query: {query}")
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
            
            try:
                logger.info("Generating response from LLM...")
                answer = self.llm_service.generate_response(query, context_str)
            except Exception as llm_err:
                logger.error(f"LLM Generation Failed: {llm_err}")
                return {"response": "AI model response dene mein nakam raha. API Key check karein.", "status": "error"}

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
                        "bookId": bookId,
                        "embedding_id": c.context_id
                    } for c in retrieved_contexts
                ],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as global_err:
            # Ye line aapko Railway logs mein asli wajah batayegi
            logger.error(f"CRITICAL ERROR in RAGService: {global_err}", exc_info=True)
            return {
                "response": f"Server par ek masla pesh aya hai: {str(global_err)}",
                "status": "error"
            }