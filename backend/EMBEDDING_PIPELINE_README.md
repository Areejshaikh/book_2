# Embedding Pipeline for Deploy Book

This project contains a complete embedding pipeline that fetches content from the Deploy Book website, processes it, and stores embeddings for retrieval.

## Overview

The pipeline performs the following steps:
1. Fetches content from the Deploy Book website (`https://book-2-bay.vercel.app/`)
2. Extracts and cleans the text content
3. Chunks the text into manageable segments
4. Generates embeddings (simulated in this version due to API key issues)
5. Stores the embeddings in a local FAISS index and metadata in JSON format

## Files Created

- `embeddings/embeddings.index` - FAISS index containing the vector embeddings
- `embeddings/metadata_YYYYMMDD_HHMMSS.json` - JSON file containing metadata for each chunk

## How to Use the Embeddings

### Loading the FAISS Index

```python
import faiss
import json
import numpy as np

# Load the FAISS index
index = faiss.read_index("embeddings/embeddings.index")

# Load the metadata
with open("embeddings/metadata_YYYYMMDD_HHMMSS.json", "r") as f:
    metadata = json.load(f)

# Example: Perform similarity search
def search_similar(query_embedding, k=5):
    # Normalize the query embedding for cosine similarity
    faiss.normalize_L2(query_embedding.reshape(1, -1))
    
    # Search for similar vectors
    scores, indices = index.search(query_embedding.reshape(1, -1), k)
    
    results = []
    for i in range(len(indices[0])):
        idx = indices[0][i]
        score = scores[0][i]
        if idx < len(metadata):
            results.append({
                'content': metadata[idx]['content'],
                'source_url': metadata[idx]['source_url'],
                'score': float(score),
                'chunk_index': metadata[idx]['chunk_index']
            })
    
    return results
```

## Running the Pipeline

To run the pipeline again:

```bash
python run_local_embedding_pipeline.py
```

## Troubleshooting

If you have valid Cohere and Qdrant API keys, you can update the `.env` file with your credentials and run the original pipeline:

```bash
python run_embedding_pipeline.py
```

This will attempt to use the online services but fall back to local storage if there are issues with the API keys.

## Dependencies

- requests
- beautifulsoup4
- faiss-cpu
- numpy
- python-dotenv