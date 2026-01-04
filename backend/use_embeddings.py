import faiss
import json
import numpy as np
import os
from typing import List, Dict


def load_embeddings():
    """
    Load the FAISS index and metadata
    """
    # Load the FAISS index
    index = faiss.read_index("embeddings/embeddings.index")

    # Find the most recent metadata file
    metadata_files = [f for f in os.listdir("embeddings") if f.startswith("metadata_") and f.endswith(".json")]
    if not metadata_files:
        raise FileNotFoundError("No metadata files found in embeddings directory")

    # Get the most recent file
    metadata_files.sort(key=lambda x: os.path.getmtime(os.path.join("embeddings", x)), reverse=True)
    latest_metadata_file = metadata_files[0]

    # Load the metadata
    with open(f"embeddings/{latest_metadata_file}", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def search_similar(index, metadata, query_embedding, k=5):
    """
    Search for similar embeddings in the FAISS index
    """
    # Normalize the query embedding for cosine similarity
    faiss.normalize_L2(query_embedding.reshape(1, -1))

    # Search for similar vectors
    scores, indices = index.search(query_embedding.reshape(1, -1), k)

    results = []
    for i in range(len(indices[0])):
        idx = indices[0][i]
        score = scores[0][i]
        if idx < len(metadata):
            # Clean content to handle special characters
            content = metadata[idx]['content']
            # Replace problematic characters or encode them
            clean_content = content.encode('utf-8', errors='ignore').decode('utf-8')
            clean_content = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content

            results.append({
                'content': clean_content,
                'source_url': metadata[idx]['source_url'],
                'score': float(score),
                'chunk_index': metadata[idx]['chunk_index']
            })

    return results


def simulate_query_embedding():
    """
    Simulate generating an embedding for a query
    In a real application, this would use an embedding model like Cohere
    """
    # Generate a random embedding vector (768 dimensions to match our stored embeddings)
    return np.random.random(768).astype('float32')


def main():
    """
    Main function to demonstrate using the generated embeddings
    """
    print("Loading embeddings...")
    index, metadata = load_embeddings()

    print(f"Loaded FAISS index with {index.ntotal} vectors")
    print(f"Loaded metadata for {len(metadata)} chunks")

    # Simulate a query
    print("\nSimulating a query embedding...")
    query_embedding = simulate_query_embedding()

    print("Searching for similar content...")
    results = search_similar(index, metadata, query_embedding, k=3)

    print(f"\nTop {len(results)} similar chunks:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.4f}")
        print(f"   Source: {result['source_url']}")
        print(f"   Chunk Index: {result['chunk_index']}")
        # Encode content to handle special characters in console output
        content_preview = result['content'].encode('ascii', errors='replace').decode('ascii')
        print(f"   Content Preview: {content_preview}")

    print("\nEmbedding pipeline completed successfully!")


if __name__ == "__main__":
    main()