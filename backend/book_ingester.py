import os
import json
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_vectors")


def process_book_data_to_qdrant():
    """
    Process book data from local storage and upload to Qdrant collection 'textbook_vectors'
    """
    global COLLECTION_NAME
    
    # Validate configuration
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("Error: QDRANT_URL and QDRANT_API_KEY environment variables must be set")
        return False

    print(f"QDRANT_URL: {QDRANT_URL}")
    print(f"Target Collection: {COLLECTION_NAME}")

    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            prefer_grpc=False
        )

        print("Connected to Qdrant successfully!")

        # Find the most recent metadata file containing book embeddings
        embeddings_dir = Path("embeddings")
        metadata_files = [f for f in embeddings_dir.iterdir() if f.name.startswith("metadata_") and f.name.endswith(".json")]

        if not metadata_files:
            print("No metadata files found in embeddings directory")
            print("Looking for potential book data files...")
            
            # Look for other potential data files
            data_files = list(embeddings_dir.glob("*.json"))
            if data_files:
                print(f"Found potential data files: {[f.name for f in data_files]}")
            else:
                print("No JSON files found in embeddings directory")
            return False

        # Get the most recent file
        latest_metadata_file = max(metadata_files, key=lambda x: x.stat().st_mtime)
        print(f"Loading book data from: {latest_metadata_file}")

        # Load the book data
        with open(latest_metadata_file, "r", encoding="utf-8") as f:
            book_data = json.load(f)

        print(f"Loaded book data for {len(book_data)} chunks")

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
            
            # Optionally clear the collection if needed
            user_input = input(f"Do you want to clear the existing collection '{COLLECTION_NAME}'? (y/N): ")
            if user_input.lower() == 'y':
                print("Deleting existing collection...")
                client.delete_collection(COLLECTION_NAME)
                collection_exists = False

        if not collection_exists:
            print(f"Creating collection '{COLLECTION_NAME}'...")
            # Create the collection with the correct vector size (768 for Cohere multilingual-v2.0)
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=768,  # Standard size for text embeddings
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{COLLECTION_NAME}' created successfully")

        # Prepare points for Qdrant
        points = []
        for i, chunk in enumerate(book_data):
            point = models.PointStruct(
                id=i,
                vector=chunk.get('embedding', []),
                payload={
                    'content': chunk.get('content', ''),
                    'source_url': chunk.get('source_url', ''),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'metadata': chunk.get('metadata', {}),
                    'book_id': chunk.get('book_id', 'default_book'),  # Add book identifier
                    **chunk.get('metadata', {})  # Additional metadata
                }
            )
            points.append(point)

        # Upload points to Qdrant in batches to avoid memory issues
        print(f"Uploading {len(points)} points to Qdrant...")
        
        # Batch upload to avoid memory issues
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

        print(f"Successfully uploaded {len(points)} points to collection '{COLLECTION_NAME}'")

        # Verify the upload
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"Final collection vectors count: {collection_info.points_count}")

        print("Book data ingestion to Qdrant completed successfully!")
        return True

    except Exception as e:
        print(f"Error processing book data to Qdrant: {str(e)}")
        print("Make sure your Qdrant credentials are correct and you have the necessary permissions.")
        return False


def validate_environment():
    """
    Validate that required environment variables are set
    """
    missing_vars = []
    if not QDRANT_URL:
        missing_vars.append("QDRANT_URL")
    if not QDRANT_API_KEY:
        missing_vars.append("QDRANT_API_KEY")
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    return True


if __name__ == "__main__":
    print("Starting book data ingestion to Qdrant...")
    
    if not validate_environment():
        sys.exit(1)
    
    success = process_book_data_to_qdrant()
    
    if success:
        print("✅ Book data successfully ingested into Qdrant collection 'textbook_vectors'")
    else:
        print("❌ Book data ingestion failed")
        sys.exit(1)