from typing import List, Optional
from qdrant_client import QdrantClient
import google.generativeai as genai
from ..models.chat_response import RetrievedContext

class QdrantRetrievalService:
    def __init__(self):
        self.url = "https://0ebab0e9-2f0f-4e48-affa-9e1ce491b5b8.us-east4-0.gcp.cloud.qdrant.io:6333"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.nR6XOHnDVIDBGzMC4y-uDlCUm0EBh53Z5bDt32uh6_E"
        self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=60)
        genai.configure(api_key="AIzaSyBw3bWN_nVmTQWPC3il4h97-Gj8usNquZ4")
        self.model_name = "models/text-embedding-004"
        self.collection_name = "deploy_book_embeddings"

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
                # FIXED: Added missing book_id and embedding_id fields
                contexts.append(RetrievedContext(
                    context_id=str(res.id),
                    chunk_text=res.payload.get("chunk_text", ""), 
                    similarity_score=res.score,
                    book_id=book_id or "default-book",
                    embedding_id=str(res.id)
                ))
            return contexts
        except Exception as e:
            print(f"DEBUG: Qdrant Search Error: {e}")
            return []

    def bypass_retrieval_for_selected_text(self, selected_text: str, book_id: str = None) -> List[RetrievedContext]:
        # FIXED: Added missing fields here as well
        return [RetrievedContext(
            context_id="selected",
            chunk_text=selected_text,
            similarity_score=1.0,
            book_id=book_id or "default-book",
            embedding_id="selected-01"
        )]

qdrant_manager = QdrantRetrievalService()