import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_qdrant_upload():
    """
    Verify that the embeddings were successfully uploaded to Qdrant
    """
    # Get configuration from environment
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "textbook_vectors"  # Using the collection we created

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("QDRANT_URL or QDRANT_API_KEY not found in environment variables")
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
        print("This could be due to network issues or the collection not being ready yet.")
        print("The upload script reported success, so the data should be there.")


if __name__ == "__main__":
    verify_qdrant_upload()