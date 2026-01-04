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
    # Configuration
    QDRANT_URL = "https://0ebab0e9-2f0f-4e48-affa-9e1ce491b5b8.us-east4-0.gcp.cloud.qdrant.io:6333"
    QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.nR6XOHnDVIDBGzMC4y-uDlCUm0EBh53Z5bDt32uh6_E"
    COLLECTION_NAME = "deploy_book_embeddings"

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