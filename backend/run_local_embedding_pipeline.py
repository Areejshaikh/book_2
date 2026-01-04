import sys
import os
from typing import List, Dict
import uuid
from datetime import datetime
import json
import faiss
import numpy as np
from pathlib import Path

# Add the backend/src directory to the Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.embedding_pipeline.config import Config, validate_config
from src.embedding_pipeline.url_fetcher import get_all_urls
from src.embedding_pipeline.text_cleaner import extract_text_from_urls
from src.embedding_pipeline.chunker import chunk_text
from src.embedding_pipeline.models import DocumentChunk
from src.embedding_pipeline.logging_config import logger


def main():
    """
    Main function to orchestrate the complete embedding pipeline using local storage:
    1. Fetch URLs
    2. Extract text content
    3. Chunk the text
    4. Simulate embeddings (since API keys are invalid)
    5. Store in local FAISS index and metadata JSON
    """
    # Validate configuration first
    if not validate_config():
        logger.error("Configuration validation failed. Please check your environment variables.")
        return

    logger.info("Starting embedding pipeline with local storage...")

    try:
        # 1. Get all URLs to process
        urls = get_all_urls()
        logger.info(f"Processing {len(urls)} URLs: {urls}")

        # 2. Extract text content from URLs
        url_to_content = extract_text_from_urls(urls)

        # 3. Process each URL's content
        all_chunks_with_embeddings = []

        for url, content in url_to_content.items():
            if not content.strip():
                logger.warning(f"No content extracted from {url}, skipping")
                continue

            logger.info(f"Processing content from {url} ({len(content)} characters)")

            # 4. Chunk the text
            text_chunks = chunk_text(content)
            logger.info(f"Text from {url} chunked into {len(text_chunks)} parts")

            # 5. Simulate embeddings for each chunk (since API keys are invalid)
            for idx, chunk_content in enumerate(text_chunks):
                if not chunk_content.strip():
                    continue  # Skip empty chunks

                # Create DocumentChunk instance
                chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{url}#{idx}"))
                doc_chunk = DocumentChunk(
                    id=chunk_id,
                    content=chunk_content,
                    source_url=url,
                    chunk_index=idx
                )

                if not doc_chunk.validate():
                    logger.warning(f"Document chunk {chunk_id} failed validation, skipping")
                    continue

                # Simulate embedding for the chunk (using random vector since API unavailable)
                # In a real scenario, this would come from an embedding model like Cohere
                simulated_embedding = np.random.random(768).astype('float32').tolist()  # 768-dim vector

                # Prepare data for local storage
                chunk_data = {
                    'id': chunk_id,
                    'content': chunk_content,
                    'source_url': url,
                    'chunk_index': idx,
                    'embedding': simulated_embedding,
                    'metadata': {
                        'created_at': datetime.now().isoformat(),
                        'source_url': url,
                        'chunk_index': idx
                    }
                }

                all_chunks_with_embeddings.append(chunk_data)

                logger.debug(f"Processed chunk {idx} for {url}")

        # 6. Save all chunks to local FAISS index and metadata JSON
        if all_chunks_with_embeddings:
            logger.info(f"Saving {len(all_chunks_with_embeddings)} chunks to local storage")
            
            # Create embeddings directory if it doesn't exist
            os.makedirs('embeddings', exist_ok=True)
            
            # Save embeddings to FAISS index
            save_embeddings_to_faiss(all_chunks_with_embeddings)
            
            # Save metadata to JSON file
            save_metadata_to_json(all_chunks_with_embeddings)
            
            logger.info(f"Successfully saved {len(all_chunks_with_embeddings)} chunks to local storage")
        else:
            logger.warning("No chunks to save")

        logger.info("Embedding pipeline completed successfully with local storage")

    except Exception as e:
        logger.error(f"Embedding pipeline failed with error: {str(e)}")
        raise


def save_embeddings_to_faiss(chunks_with_embeddings: List[Dict]):
    """
    Save embeddings to a local FAISS index
    """
    # Extract embeddings as numpy array
    embeddings = np.array([chunk['embedding'] for chunk in chunks_with_embeddings]).astype('float32')
    
    # Create FAISS index (Inner Product for similarity search)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity after normalization)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Add embeddings to index
    index.add(embeddings)
    
    # Save the index
    faiss.write_index(index, "embeddings/embeddings.index")
    
    logger.info(f"Saved FAISS index with {len(chunks_with_embeddings)} vectors")


def save_metadata_to_json(chunks_with_embeddings: List[Dict]):
    """
    Save metadata to a JSON file
    """
    # Save metadata to a JSON file
    filename = f"embeddings/metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(chunks_with_embeddings, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved metadata for {len(chunks_with_embeddings)} chunks to {filename}")


if __name__ == "__main__":
    main()