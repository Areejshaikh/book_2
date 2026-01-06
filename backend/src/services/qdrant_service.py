import os
from typing import List, Optional
from qdrant_client import QdrantClient
import google.generativeai as genai
from ..models.chat_response import RetrievedContext

class QdrantRetrievalService:
    def __init__(self):
        # ❌ Purani hardcoded keys yahan se khatam kar di hain
        # ✅ Ab ye code Railway ke "Variables" tab se keys pick karega
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        
        # Qdrant Client Setup
        self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=60)
        
        # Gemini API Key for Embeddings
        google_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=google_key)
        
        self.model_name = "models/text-embedding-004"
        self.collection_name = "textbook_vectors"

    def search_relevant_chunks(self, query: str, book_id: str = None, top_k: int = 5) -> List[RetrievedContext]:
        try:
            result = genai.embed_content(model=self.model_name, content=query)
            query_vector = result['embedding']

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k 
            )

            contexts = []
            for res in search_results:
                contexts.append(RetrievedContext(
                    context_id=str(res.id),
                    chunk_text=res.payload.get("chunk_text", ""), 
                    similarity_score=res.score,
                    book_id=book_id or "default-book",
                    embedding_id=str(res.id)
                ))
            return contexts
        except Exception as e:
            # Ye error ab tabhi aayega jab keys ghalat hongi
            print(f"DEBUG: Qdrant Search Error: {e}")
            return []

    def bypass_retrieval_for_selected_text(self, selected_text: str, book_id: str = None) -> List[RetrievedContext]:
        return [RetrievedContext(
            context_id="selected",
            chunk_text=selected_text,
            similarity_score=1.0,
            book_id=book_id or "default-book",
            embedding_id="selected-01"
        )]

qdrant_manager = QdrantRetrievalService()