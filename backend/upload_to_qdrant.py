import json
import os
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict

# Add the backend/src directory to the Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.embedding_pipeline.config import Config


def upload_embeddings_to_qdrant():
    """
    Upload embeddings from local storage to Qdrant
    """
    # Validate configuration first
    errors = Config.validate()
    if errors:
        print("Configuration validation failed. Please check your environment variables:")
        for error in errors:
            print(f"  - {error}")
        return

    print(f"QDRANT_URL: {Config.QDRANT_URL}")
    print(f"QDRANT_COLLECTION_NAME: {Config.COLLECTION_NAME}")

    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY,
            prefer_grpc=False
        )

        print("Connected to Qdrant successfully!")

        # Find the most recent metadata file
        embeddings_dir = Path("embeddings")
        metadata_files = [f for f in embeddings_dir.iterdir() if f.name.startswith("metadata_") and f.name.endswith(".json")]

        if not metadata_files:
            print("No metadata files found in embeddings directory")
            return

        # Get the most recent file
        latest_metadata_file = max(metadata_files, key=lambda x: x.stat().st_mtime)
        print(f"Loading embeddings from: {latest_metadata_file}")

        # Load the metadata
        with open(latest_metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        print(f"Loaded metadata for {len(metadata)} chunks")

        # Use a new collection name to avoid permission issues
        collection_name = "deploy_book_embeddings"

        # Check if collection exists
        collections = client.get_collections()
        collection_exists = any(collection.name == collection_name for collection in collections.collections)

        if collection_exists:
            print(f"Collection '{collection_name}' already exists")
            # Get collection info
            collection_info = client.get_collection(collection_name)
            print(f"Current collection vectors count: {collection_info.points_count}")
            print(f"Current collection vector size: {collection_info.config.params.vectors.size}")
            print(f"Current collection distance: {collection_info.config.params.vectors.distance}")
        else:
            print(f"Collection '{collection_name}' does not exist, creating it...")

            # Create the collection with the correct vector size (768 for Cohere multilingual-v2.0)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=768,  # Cohere multilingual-v2.0 model returns 768-dimension vectors
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{collection_name}' created successfully")

        # Prepare points for Qdrant
        points = []
        for i, chunk in enumerate(metadata):
            point = models.PointStruct(
                # Use the chunk's actual ID if available, otherwise use the index
                id=i,
                vector=chunk.get('embedding', []),
                payload={
                    'content': chunk.get('content', ''),
                    'source_url': chunk.get('source_url', ''),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'metadata': chunk.get('metadata', {}),
                    **chunk.get('metadata', {})  # Additional metadata
                }
            )
            points.append(point)

        # Upload points to Qdrant
        print(f"Uploading {len(points)} points to Qdrant...")
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        print(f"Successfully uploaded {len(points)} points to collection '{collection_name}'")

        # Verify the upload
        collection_info = client.get_collection(collection_name)
        print(f"Final collection vectors count: {collection_info.points_count}")

        print("Embedding upload to Qdrant completed successfully!")

    except Exception as e:
        print(f"Error uploading embeddings to Qdrant: {str(e)}")
        print("Make sure your Qdrant credentials are correct and you have the necessary permissions.")


if __name__ == "__main__":
    upload_embeddings_to_qdrant()