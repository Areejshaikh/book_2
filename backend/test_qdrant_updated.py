import sys
import os

# Add the backend/src directory to the Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.embedding_pipeline.config import Config
from src.embedding_pipeline.vector_store import QdrantStore

print(f"QDRANT_URL: {Config.QDRANT_URL}")
print(f"QDRANT_API_KEY: {'Set' if Config.QDRANT_API_KEY else 'Not set'}")
print(f"QDRANT_COLLECTION_NAME: {Config.COLLECTION_NAME}")

try:
    # Create Qdrant store instance
    qdrant_store = QdrantStore()
    
    # Test connection by listing collections
    collections = qdrant_store.client.get_collections()
    print("Connected to Qdrant successfully!")
    print(f"Available collections: {[collection.name for collection in collections.collections]}")
    
    # Check if our collection exists
    collection_exists = any(collection.name == Config.COLLECTION_NAME for collection in collections.collections)
    if collection_exists:
        print(f"Collection '{Config.COLLECTION_NAME}' exists")
        
        # Get collection info
        collection_info = qdrant_store.client.get_collection(Config.COLLECTION_NAME)
        print(f"Collection vectors count: {collection_info.points_count}")
        print(f"Collection vector size: {collection_info.config.params.vectors.size}")
        print(f"Collection distance: {collection_info.config.params.vectors.distance}")
    else:
        print(f"Collection '{Config.COLLECTION_NAME}' does not exist")
    
except Exception as e:
    print(f"Error connecting to Qdrant: {str(e)}")