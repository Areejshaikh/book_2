"""
URL Ingestion & Embedding Pipeline (Updated & Fixed)

تبدیلیاں:
- Vector size 4096 → 1024 (Cohere کے مطابق)
- بہتر Docusaurus content selectors (article first)
- بہتر chunking with semantic boundaries
- Multiple sitemaps support
- Retry logic for Cohere embeddings
- Duplicate URLs removal
"""

import os
import re
import time
import logging
import argparse
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct
import hashlib
import tenacity  # pip install tenacity اگر نہیں ہے تو

from config.settings import load_config_from_env, PipelineConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CrawledContent:
    url: str
    title: str
    content: str
    metadata: Dict


@dataclass
class TextChunk:
    id: str
    content: str
    source_url: str
    source_title: str
    chunk_index: int
    metadata: Dict


class DocusaurusCrawler:
    def __init__(self, max_pages: int = 1000):
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_sitemap_urls(self, base_url: str) -> List[str]:
        """Multiple possible sitemaps چیک کرتا ہے"""
        possible_sitemaps = ['sitemap.xml', 'sitemap-pages.xml', 'sitemap-blog.xml', 'sitemap-0.xml']
        urls = set()

        for sm in possible_sitemaps:
            sitemap_url = urljoin(base_url, sm)
            try:
                response = self.session.get(sitemap_url, timeout=60)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    for loc in soup.find_all('loc'):
                        url = loc.text.strip()
                        if url.startswith(base_url):
                            urls.add(url)
                    logger.info(f"Found {len(urls)} URLs from {sm}")
            except Exception as e:
                logger.debug(f"Sitemap {sitemap_url} not found or error: {e}")

        return list(urls)

    def crawl_url(self, url: str) -> Optional[CrawledContent]:
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for elem in soup(["script", "style", "nav", "header", "footer", "aside"]):
                elem.decompose()

            # Better selectors for Docusaurus (article is most reliable)
            content_selectors = [
                'article',  # سب سے بہتر
                'div.theme-doc-markdown',
                'div.markdown',
                'main div[class*="docItem"]',
                'div[class*="docItemContainer"]',
                'div[class*="markdown"]',
                '[role="main"]',
                'main',
            ]

            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break

            if not content_element:
                content_element = soup.find('body')

            content = content_element.get_text(separator=' ', strip=True) if content_element else ""
            content = re.sub(r'\s+', ' ', content).strip()

            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else urlparse(url).path.split('/')[-1] or 'No Title'

            metadata = {
                'crawl_timestamp': time.time(),
                'url': url,
            }

            return CrawledContent(url=url, title=title, content=content, metadata=metadata)

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None

    def crawl_urls(self, urls: List[str]) -> List[CrawledContent]:
        crawled_contents = []
        seen_urls = set()

        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            logger.info(f"Crawling: {url}")
            content = self.crawl_url(url)
            if content and content.content.strip():
                crawled_contents.append(content)
            time.sleep(0.5)

            if len(crawled_contents) >= self.max_pages:
                break

        return crawled_contents


class TextProcessor:
    def __init__(self, chunk_size: int = 512, overlap: float = 0.2):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chars_per_token = 4

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, content: str, source_url: str, source_title: str) -> List[TextChunk]:
        content = self.clean_text(content)
        if not content:
            return []

        max_chars = int(self.chunk_size * self.chars_per_token)
        overlap_chars = int(max_chars * self.overlap)

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(content):
            end = start + max_chars
            chunk_text = content[start:end]

            if end < len(content):
                # Better boundary تلاش کریں
                boundary = max(
                    chunk_text.rfind('. '),
                    chunk_text.rfind('! '),
                    chunk_text.rfind('? '),
                    chunk_text.rfind('\n\n'),
                    chunk_text.rfind(' '),
                )
                if boundary > max_chars // 2:
                    chunk_text = chunk_text[:boundary + 1]
                    end = start + len(chunk_text)

            if chunk_text.strip():
                chunk_id = hashlib.md5(f"{source_url}_{chunk_index}".encode()).hexdigest()
                chunks.append(TextChunk(
                    id=chunk_id,
                    content=chunk_text.strip(),
                    source_url=source_url,
                    source_title=source_title,
                    chunk_index=chunk_index,
                    metadata={}
                ))

            start = end - overlap_chars
            if start >= len(content):
                break
            chunk_index += 1

        return chunks


class Embedder:
    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):  # v3 تجویز کیا جاتا ہے
        self.client = cohere.Client(api_key)
        self.model = model

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document",  # v3+ کے لیے بہتر
                truncate="END"
            )
            return response.embeddings
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise


class VectorStore:
    def __init__(self, url: str, api_key: str, collection_name: str = "book_embeddings"):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self._create_collection()

    def _create_collection(self):
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            )
            logger.info(f"Created collection '{self.collection_name}' with dimension 1024")

    def store_embeddings(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> bool:
        if len(chunks) != len(embeddings):
            logger.error("Chunks and embeddings count mismatch")
            return False

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(PointStruct(
                id=chunk.id,
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "source_url": chunk.source_url,
                    "source_title": chunk.source_title,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata
                }
            ))

        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Stored {len(points)} vectors")
            return True
        except Exception as e:
            logger.error(f"Qdrant upsert error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='URL Ingestion & Embedding Pipeline')
    parser.add_argument('--urls', nargs='+', required=True, help='Base URLs (e.g. https://example.com/docs/)')
    parser.add_argument('--chunk-size', type=int, default=512)
    parser.add_argument('--overlap', type=float, default=0.2)
    parser.add_argument('--embed-model', default='embed-english-v3.0')
    parser.add_argument('--collection-name', default='book_embeddings')
    parser.add_argument('--batch-size', type=int, default=96)

    args = parser.parse_args()

    try:
        config = load_config_from_env()
        config.chunk_size = args.chunk_size or config.chunk_size
        config.overlap = args.overlap or config.overlap
        config.embed_model = args.embed_model or config.embed_model
        config.collection_name = args.collection_name or config.collection_name
        config.batch_size = args.batch_size or config.batch_size
    except ValueError as e:
        logger.error(f"Config error: {e}")
        return

    crawler = DocusaurusCrawler(max_pages=config.max_pages)
    processor = TextProcessor(chunk_size=config.chunk_size, overlap=config.overlap)
    embedder = Embedder(api_key=config.cohere_api_key, model=config.embed_model)
    vector_store = VectorStore(url=config.qdrant_url, api_key=config.qdrant_api_key,
                               collection_name=config.collection_name)

    all_crawled_content = []
    for base_url in args.urls:
        site_urls = crawler.get_sitemap_urls(base_url) or [base_url]
        crawled = crawler.crawl_urls(site_urls)
        all_crawled_content.extend(crawled)

    logger.info(f"Crawled {len(all_crawled_content)} pages")

    all_chunks = []
    for content in all_crawled_content:
        chunks = processor.chunk_text(content.content, content.url, content.title)
        all_chunks.extend(chunks)

    logger.info(f"Created {len(all_chunks)} chunks")

    all_embeddings = []
    for i in range(0, len(all_chunks), config.batch_size):
        batch = all_chunks[i:i + config.batch_size]
        texts = [c.content for c in batch]
        embeddings = embedder.generate_embeddings(texts)
        all_embeddings.extend(embeddings)

    success = vector_store.store_embeddings(all_chunks, all_embeddings)

    if success:
        logger.info("Pipeline completed successfully!")
    else:
        logger.error("Pipeline failed at storage")


if __name__ == "__main__":
    main()