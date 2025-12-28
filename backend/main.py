"""
URL Ingestion & Embedding Pipeline

This script implements a complete pipeline that:
1. Collects and validates Docusaurus URLs
2. Crawls the content from these URLs
3. Cleans and chunks the text
4. Generates embeddings using Cohere
5. Stores vectors and metadata in Qdrant
"""

import os
import re
import time
import logging
import argparse
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct
import hashlib

from config.settings import load_config_from_env, PipelineConfig


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CrawledContent:
    """Represents the extracted text from a single URL"""
    url: str
    title: str
    content: str
    metadata: Dict


@dataclass
class TextChunk:
    """A segment of text from CrawledContent that fits within embedding model constraints"""
    id: str
    content: str
    source_url: str
    source_title: str
    chunk_index: int
    metadata: Dict


class DocusaurusCrawler:
    """Crawls Docusaurus documentation sites and extracts content"""

    def __init__(self, max_pages: int = 1000):
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_sitemap_urls(self, base_url: str) -> List[str]:
        """Extract URLs from sitemap.xml if available"""
        sitemap_url = urljoin(base_url, 'sitemap.xml')
        try:
            response = self.session.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                urls = []
                for loc in soup.find_all('loc'):
                    url = loc.text.strip()
                    if url.startswith(base_url):
                        urls.append(url)
                logger.info(f"Found {len(urls)} URLs in sitemap")
                return urls
        except Exception as e:
            logger.warning(f"Could not fetch sitemap from {sitemap_url}: {e}")

        return []

    def crawl_url(self, url: str) -> Optional[CrawledContent]:
        """Crawl a single URL and extract content"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find the main content area in Docusaurus sites
            # Common selectors for Docusaurus content areas
            content_selectors = [
                'main div[class*="docItem"]',  # Docusaurus doc item
                'article',  # Standard article tag
                'main',  # Main content area
                'div[class*="container"]',  # Container divs
                'div[class*="doc"]',  # Doc-related divs
                'div[class*="markdown"]',  # Markdown content
                '[role="main"]',  # Main role
            ]

            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break

            # If no specific content area found, use body
            if not content_element:
                content_element = soup.find('body')

            if content_element:
                # Extract text, cleaning up newlines and extra spaces
                content = content_element.get_text(separator=' ', strip=True)
                # Clean up excessive whitespace
                content = re.sub(r'\s+', ' ', content)
            else:
                logger.warning(f"No content found for {url}")
                content = ""

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else urlparse(url).path.split('/')[-1] or 'No Title'

            # Extract metadata
            metadata = {
                'crawl_timestamp': time.time(),
                'url': url,
            }

            return CrawledContent(
                url=url,
                title=title,
                content=content,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None

    def crawl_urls(self, urls: List[str]) -> List[CrawledContent]:
        """Crawl multiple URLs and return list of crawled content"""
        crawled_contents = []

        for url in urls:
            logger.info(f"Crawling: {url}")
            content = self.crawl_url(url)
            if content:
                crawled_contents.append(content)
            time.sleep(0.5)  # Be respectful to the server

        return crawled_contents


class TextProcessor:
    """Processes text by cleaning and chunking it"""

    def __init__(self, chunk_size: int = 512, overlap: float = 0.2):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Estimated token to character ratio (rough approximation)
        self.chars_per_token = 4

    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with embeddings
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        return text.strip()

    def chunk_text(self, content: str, source_url: str, source_title: str) -> List[TextChunk]:
        """Split content into chunks of approximately chunk_size tokens"""
        # Roughly convert tokens to characters (1 token ≈ 4 characters)
        max_chars = int(self.chunk_size * self.chars_per_token)
        overlap_chars = int(max_chars * self.overlap)

        # Split content into sentences to maintain semantic boundaries
        sentences = re.split(r'[.!?]+', content)

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If adding the next sentence would exceed the chunk size
            if len(current_chunk) + len(sentence) > max_chars:
                # Save the current chunk
                if current_chunk.strip():
                    chunk_id = hashlib.md5(f"{source_url}_{chunk_index}".encode()).hexdigest()
                    chunks.append(TextChunk(
                        id=chunk_id,
                        content=current_chunk.strip(),
                        source_url=source_url,
                        source_title=source_title,
                        chunk_index=chunk_index,
                        metadata={}
                    ))

                # Start a new chunk with some overlap
                if overlap_chars > 0:
                    # Get the end of the current chunk for overlap
                    overlap_start = max(0, len(current_chunk) - overlap_chars)
                    current_chunk = current_chunk[overlap_start:]
                else:
                    current_chunk = ""

                chunk_index += 1

            current_chunk += " " + sentence

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunk_id = hashlib.md5(f"{source_url}_{chunk_index}".encode()).hexdigest()
            chunks.append(TextChunk(
                id=chunk_id,
                content=current_chunk.strip(),
                source_url=source_url,
                source_title=source_title,
                chunk_index=chunk_index,
                metadata={}
            ))

        return chunks


class Embedder:
    """Generates embeddings using Cohere"""

    def __init__(self, api_key: str, model: str = "embed-english-v2.0"):
        self.client = cohere.Client(api_key)
        self.model = model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model
            )
            return response.embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []


class VectorStore:
    """Stores embeddings in Qdrant vector database"""

    def __init__(self, url: str, api_key: str, collection_name: str = "book_embeddings"):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """Create the collection in Qdrant if it doesn't exist"""
        try:
            # Try to get collection info to check if it exists
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=4096, distance=models.Distance.COSINE),
            )
            logger.info(f"Created collection '{self.collection_name}'")

    def store_embeddings(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> bool:
        """Store text chunks and their embeddings in Qdrant"""
        if len(chunks) != len(embeddings):
            logger.error("Number of chunks and embeddings don't match")
            return False

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point = PointStruct(
                id=chunk.id,
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "source_url": chunk.source_url,
                    "source_title": chunk.source_title,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata
                }
            )
            points.append(point)

        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Successfully stored {len(points)} vectors in Qdrant")
            return True
        except Exception as e:
            logger.error(f"Error storing embeddings in Qdrant: {e}")
            return False


def main():
    """Main function that orchestrates the entire pipeline"""
    parser = argparse.ArgumentParser(description='URL Ingestion & Embedding Pipeline')
    parser.add_argument('--urls', nargs='+', required=True, help='List of Docusaurus URLs to process')
    parser.add_argument('--chunk-size', type=int, help='Size of text chunks in tokens')
    parser.add_argument('--overlap', type=float, help='Overlap between chunks as percentage')
    parser.add_argument('--embed-model', help='Cohere model to use for embeddings')
    parser.add_argument('--collection-name', help='Qdrant collection name')
    parser.add_argument('--batch-size', type=int, help='Number of chunks to process in each batch')

    args = parser.parse_args()

    logger.info("Starting URL Ingestion & Embedding Pipeline")

    # Load configuration
    try:
        config = load_config_from_env()

        # Override config values with command line arguments if provided
        if args.chunk_size is not None:
            config.chunk_size = args.chunk_size
        if args.overlap is not None:
            config.overlap = args.overlap
        if args.embed_model is not None:
            config.embed_model = args.embed_model
        if args.collection_name is not None:
            config.collection_name = args.collection_name
        if args.batch_size is not None:
            config.batch_size = args.batch_size
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Initialize components with configuration
    crawler = DocusaurusCrawler(max_pages=config.max_pages)
    processor = TextProcessor(chunk_size=config.chunk_size, overlap=config.overlap)
    embedder = Embedder(
        api_key=config.cohere_api_key,
        model=config.embed_model
    )
    vector_store = VectorStore(
        url=config.qdrant_url,
        api_key=config.qdrant_api_key,
        collection_name=config.collection_name
    )

    # Step 1: Crawl URLs
    logger.info("Step 1: Crawling URLs")
    all_crawled_content = []

    for url in args.urls:
        logger.info(f"Processing site: {url}")
        # Try to get URLs from sitemap first
        site_urls = crawler.get_sitemap_urls(url)

        if site_urls:
            crawled_content = crawler.crawl_urls(site_urls)
        else:
            # If no sitemap, just crawl the provided URL
            content = crawler.crawl_url(url)
            if content:
                crawled_content = [content]
            else:
                crawled_content = []

        all_crawled_content.extend(crawled_content)

    logger.info(f"Crawled {len(all_crawled_content)} pages")

    # Step 2: Process and chunk content
    logger.info("Step 2: Processing and chunking content")
    all_chunks = []

    for content in all_crawled_content:
        chunks = processor.chunk_text(content.content, content.url, content.title)
        all_chunks.extend(chunks)

    logger.info(f"Created {len(all_chunks)} text chunks")

    # Step 3: Generate embeddings in batches
    logger.info("Step 3: Generating embeddings")
    all_embeddings = []

    for i in range(0, len(all_chunks), config.batch_size):
        batch_chunks = all_chunks[i:i + config.batch_size]
        batch_texts = [chunk.content for chunk in batch_chunks]

        logger.info(f"Processing batch {i//config.batch_size + 1}/{(len(all_chunks)-1)//config.batch_size + 1}")
        batch_embeddings = embedder.generate_embeddings(batch_texts)
        all_embeddings.extend(batch_embeddings)

    logger.info(f"Generated {len(all_embeddings)} embeddings")

    # Step 4: Store in Qdrant
    logger.info("Step 4: Storing embeddings in Qdrant")
    success = vector_store.store_embeddings(all_chunks, all_embeddings)

    if success:
        logger.info("Pipeline completed successfully!")
        print(f"Successfully processed {len(all_crawled_content)} pages and stored {len(all_embeddings)} embeddings in Qdrant")
    else:
        logger.error("Pipeline failed during storage step")
        print("Pipeline failed during storage step")


if __name__ == "__main__":
    main()