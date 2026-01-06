# Book Data Ingestion for Qdrant

This script processes book data and ingests it into a Qdrant vector database collection named `textbook_vectors`.

## Files

- `book_ingester.py`: Main script to process book data from local storage and upload to Qdrant
- `simple_ingest.py`: Script to scrape book content from URLs and directly upload to Qdrant

## Prerequisites

1. Python 3.8+
2. Required Python packages (from requirements.txt)
3. Environment variables set in `.env` file:
   - `QDRANT_URL`: URL to your Qdrant instance
   - `QDRANT_API_KEY`: API key for Qdrant
   - `QDRANT_COLLECTION_NAME`: Collection name (defaults to "textbook_vectors")

## Usage

### Using the book ingester (from local data):

```bash
cd backend
python book_ingester.py
```

This will:
1. Look for the most recent metadata file in the `embeddings` directory
2. Process the book data (content + embeddings) from that file
3. Upload it to the specified Qdrant collection

### Using the simple ingester (from web scraping):

```bash
cd backend
python simple_ingest.py
```

This will:
1. Scrape content from the specified URLs
2. Generate embeddings using Google's text-embedding-004 model
3. Upload the content and embeddings to Qdrant

## Configuration

The collection is created with:
- Vector size: 768 (compatible with Cohere multilingual-v2.0 and Google text-embedding-004)
- Distance metric: Cosine similarity
- Payload includes: content, source URL, chunk index, and metadata

## Notes

- The script handles batching to avoid memory issues with large datasets
- Existing collections can be cleared before ingestion if needed
- The script provides progress updates during the ingestion process