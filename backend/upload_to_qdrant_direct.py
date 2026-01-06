import json
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
from urllib.parse import urlparse
import requests


def upload_embeddings_to_qdrant():
    """
    Upload embeddings from local storage to Qdrant with better error handling
    """
    import os
    # Configuration - you may need to update these values
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "textbook_vectors"

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("Error: QDRANT_URL and QDRANT_API_KEY environment variables must be set")
        return

    print(f"QDRANT_URL: {QDRANT_URL}")
    print(f"COLLECTION_NAME: {COLLECTION_NAME}")

    # Check if Qdrant is accessible
    try:
        # Test basic connectivity
        health_check_url = f"{QDRANT_URL.strip('/')}/collections"
        headers = {"api-key": QDRANT_API_KEY} if QDRANT_API_KEY else {}
        response = requests.get(health_check_url, headers=headers, timeout=60)

        if response.status_code == 200:
            print("Successfully connected to Qdrant!")
        else:
            print(f"Qdrant health check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"Error connecting to Qdrant: {str(e)}")
        return

    try:
        # Initialize Qdrant client with proper URL handling
        parsed_url = urlparse(QDRANT_URL)
        https_enabled = parsed_url.scheme == 'https'

        client = QdrantClient(
            host=parsed_url.hostname,
            port=parsed_url.port,
            api_key=QDRANT_API_KEY,
            https=https_enabled
        )

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

        # Check if collection exists
        collections = client.get_collections()
        collection_exists = any(collection.name == COLLECTION_NAME for collection in collections.collections)

        if collection_exists:
            print(f"Collection '{COLLECTION_NAME}' already exists")
            # Get collection info
            collection_info = client.get_collection(COLLECTION_NAME)
            print(f"Current collection vectors count: {collection_info.points_count}")
            print(f"Current collection vector size: {collection_info.config.params.vectors.size}")
            print(f"Current collection distance: {collection_info.config.params.vectors.distance}")
        else:
            print(f"Collection '{COLLECTION_NAME}' does not exist, creating it...")

            # Create the collection with the correct vector size (768 for Cohere multilingual-v2.0)
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=768,  # Cohere multilingual-v2.0 model returns 768-dimension vectors
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{COLLECTION_NAME}' created successfully")

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
            collection_name=COLLECTION_NAME,
            points=points
        )

        print(f"Successfully uploaded {len(points)} points to collection '{COLLECTION_NAME}'")

        # Verify the upload
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"Final collection vectors count: {collection_info.points_count}")

        print("Embedding upload to Qdrant completed successfully!")

    except Exception as e:
        print(f"Error uploading embeddings to Qdrant: {str(e)}")
        print("Make sure your Qdrant credentials are correct and you have the necessary permissions.")


if __name__ == "__main__":
    upload_embeddings_to_qdrant()