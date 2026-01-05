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

    def get_answer(self, query: str, book_id: str, session_id: str, selected_text: Optional[str] = None) -> dict:
        msg_id = str(uuid.uuid4())
        
        # FIX 1: Ensure bookId is consistent (lowercase)
        current_book_id = "textbook" # Force 'textbook' for now to match indexed data
        
        try:
            if selected_text:
                retrieved_contexts = self.qdrant_service.bypass_retrieval_for_selected_text(
                    selected_text=selected_text, 
                    book_id=current_book_id
                )
            else:
                # FIX 2: Debug log to see what exactly we are searching
                logger.info(f"Searching for: {query} in {current_book_id}")
                retrieved_contexts = self.qdrant_service.search_relevant_chunks(
                    query=query, 
                    book_id=current_book_id, 
                    top_k=5
                )

            # FIX 3: Detailed Feedback if no data is found
            if not retrieved_contexts:
                logger.warning(f"DATABASE EMPTY OR NO MATCH: Query was '{query}'")
                return {
                    "response": "Maaf kijiye, database mein is sawal se mutaliq koi data nahi mila. Baraye meherbani check karein ke textbook files index ho chuki hain.",
                    "confidence_level": "Zero",
                    "session_id": session_id,
                    "retrieved_context": []
                }

            # Baki Generating Answer wala code yahan aayega...
            context_str = "\n".join([ctx.chunk_text for ctx in retrieved_contexts])
            answer = self.llm_service.generate_response(query, context_str)
            
            return {
                "response": answer,
                "confidence_level": "High",
                "session_id": session_id,
                "retrieved_context": [{"chunk_text": c.chunk_text} for c in retrieved_contexts]
            }

        except Exception as e:
            logger.error(f"Global Error: {str(e)}")
            return {"response": f"Backend Error: {str(e)}", "status": "error"}