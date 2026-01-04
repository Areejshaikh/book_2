import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

# Get Qdrant configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_vectors")

print(f"QDRANT_URL: {QDRANT_URL}")
print(f"QDRANT_COLLECTION_NAME: {QDRANT_COLLECTION_NAME}")

try:
    # Create Qdrant client
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=False
    )
    
    # Test connection by listing collections
    collections = client.get_collections()
    print("Connected to Qdrant successfully!")
    print(f"Available collections: {[collection.name for collection in collections.collections]}")
    
    # Check if our collection exists
    collection_exists = any(collection.name == QDRANT_COLLECTION_NAME for collection in collections.collections)
    if collection_exists:
        print(f"Collection '{QDRANT_COLLECTION_NAME}' exists")
        
        # Get collection info
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
        print(f"Collection vectors count: {collection_info.points_count}")
        print(f"Collection vector size: {collection_info.config.params.vectors.size}")
        print(f"Collection distance: {collection_info.config.params.vectors.distance}")
    else:
        print(f"Collection '{QDRANT_COLLECTION_NAME}' does not exist")
    
except Exception as e:
    print(f"Error connecting to Qdrant: {str(e)}")