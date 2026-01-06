import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models
import numpy as np

# Add the backend/src directory to the Python path so we can import our modules
sys.path.append('src')

from src.embedding_pipeline.config import Config


def verify_qdrant_upload():
    """
    Verify that the embeddings were successfully uploaded to Qdrant
    """
    import os
    # Configuration
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "textbook_vectors"

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("Error: QDRANT_URL and QDRANT_API_KEY environment variables must be set")
        return

    print(f"Connecting to Qdrant: {QDRANT_URL}")
    print(f"Collection: {COLLECTION_NAME}")

    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            prefer_grpc=False
        )

        # Get collection info
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists")
        print(f"Vectors count: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        print(f"Distance: {collection_info.config.params.vectors.distance}")

        # Get all points in the collection
        points = list(client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10  # Get up to 10 points
        ))

        print(f"\nRetrieved {len(points[0])} points from collection")

        for i, point in enumerate(points[0]):
            print(f"\nPoint {i+1}:")
            print(f"  ID: {point.id}")
            print(f"  Content preview: {point.payload.get('content', '')[:100]}...")
            print(f"  Source URL: {point.payload.get('source_url', '')}")
            print(f"  Chunk Index: {point.payload.get('chunk_index', '')}")

        print("\nVerification completed successfully!")

    except Exception as e:
        print(f"Error verifying Qdrant upload: {str(e)}")


if __name__ == "__main__":
    verify_qdrant_upload()