import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from urllib.parse import urljoin
import time

# 1. Configuration
BASE_URL = "https://book-2-bay.vercel.app/docs/category/textbook-modules"
GEMINI_API_KEY = "AIzaSyBw3bWN_nVmTQWPC3il4h97-Gj8usNquZ4"
QDRANT_URL = "https://0ebab0e9-2f0f-4e48-affa-9e1ce491b5b8.us-east4-0.gcp.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.nR6XOHnDVIDBGzMC4y-uDlCUm0EBh53Z5bDt32uh6_E"
COLLECTION_NAME = "deploy_book_embeddings"

genai.configure(api_key=GEMINI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def get_links(url):
    """Website se saare modules ke links nikalne ke liye"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    # Docusaurus sidebar ya main content se links dhoondna
    for a in soup.find_all('a', href=True):
        if '/docs/' in a['href']:
            links.append(urljoin(url, a['href']))
    return list(set(links)) # Unique links

def run_advanced_ingestion():
    # 1. Pehle saare links dhoondein
    print("Searching for module links...")
    all_urls = get_links(BASE_URL)
    if not all_urls:
        all_urls = [BASE_URL]
    
    print(f"Found {len(all_urls)} pages to scrape.")
    
    all_points = []
    point_id = 0

    # 2. Har link par ja kar data nikaalein
    for url in all_urls:
        print(f"Scraping content from: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Sirf kaam ka text uthana (Article content)
        content = soup.find('article') or soup.find('main')
        if not content: continue
        
        text = content.get_text(separator=' ', strip=True)
        
        # Chunks banana
        chunks = [text[i:i+1000] for i in range(0, len(text), 900)]
        
        for chunk in chunks:
            result = genai.embed_content(model="models/text-embedding-004", content=chunk)
            all_points.append(PointStruct(
                id=point_id,
                vector=result['embedding'],
                payload={"chunk_text": chunk, "source": url, "book_id": "default-book"}
            ))
            point_id += 1
        time.sleep(1) # API slow down

    # 3. Qdrant mein upload karein
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=all_points)
    print(f"✅ SUCCESS: {len(all_points)} chunks ingested from {len(all_urls)} pages!")

if __name__ == "__main__":
    run_advanced_ingestion()