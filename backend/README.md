# URL Ingestion & Embedding Pipeline

This project implements a pipeline that crawls Docusaurus documentation sites, extracts content, generates embeddings using Cohere, and stores them in Qdrant vector database.

## Features

- Crawls Docusaurus documentation sites
- Extracts and cleans content
- Chunks text appropriately
- Generates embeddings using Cohere models
- Stores vectors with metadata in Qdrant

## Setup

1. Install dependencies:
   ```bash
   uv sync
   # Or if using pip:
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file with the following:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

## Usage

Run the pipeline with:
```bash
python main.py --urls "https://example-docusaurus-site.com" "https://another-site.com"
```

For more options:
```bash
python main.py --help
```

## Configuration

- `--urls`: List of Docusaurus URLs to process (required)
- `--chunk-size`: Size of text chunks in tokens (default: 512)
- `--overlap`: Overlap between chunks as percentage (default: 0.2)
- `--embed-model`: Cohere model to use for embeddings (default: "embed-english-v2.0")
- `--collection-name`: Qdrant collection name (default: "deploy_book_embeddings")
- `--batch-size`: Number of chunks to process in each batch (default: 10)

## Edge Cases and Error Scenarios

### Crawling Issues
- **Inaccessible URLs**: If a URL is not accessible or returns an error, the crawler will log the error and continue with other URLs
- **Rate Limiting**: The crawler implements rate limiting with a 0.5-second delay between requests to be respectful to the server
- **Large Documents**: Very large documents are automatically chunked to fit within embedding model limits
- **Non-Docusaurus Sites**: The crawler tries to identify and extract content from various site types, but results may vary for non-Docusaurus sites

### Embedding Issues
- **API Errors**: If Cohere API returns an error, the pipeline will log the error and continue processing other chunks
- **Rate Limits**: The pipeline processes embeddings in batches to manage API rate limits
- **Unsupported Languages**: Content in languages not supported by the embedding model may not generate meaningful embeddings

### Storage Issues
- **Qdrant Unavailable**: If Qdrant is temporarily unavailable, the pipeline will log the error and continue processing
- **Collection Creation**: The pipeline automatically creates the Qdrant collection if it doesn't exist
- **Storage Limits**: If storage limits are reached, the pipeline will stop and report the error

### Memory and Performance
- **Memory Usage**: The pipeline is designed to keep memory usage under 512MB during processing by processing content in batches
- **Processing Time**: For large documentation sites, processing can take several hours depending on the number of pages and content size

### Network Issues
- **Timeouts**: Network requests have timeout limits (15 seconds for content, 10 seconds for sitemaps) to prevent hanging
- **Retry Mechanisms**: The pipeline implements retry mechanisms for transient network failures