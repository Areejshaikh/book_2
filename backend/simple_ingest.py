import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from urllib.parse import urljoin
import time
from dotenv import load_dotenv # Agar .env file use kar rahe hain

# .env file se variables load karne ke liye
load_dotenv()

# --- CONFIGURATION (Ab ye env se ayenge) ---
BASE_URL = "https://book-2-bay.vercel.app/docs/category/textbook-modules"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", )

# Check karein ke variables mil rahe hain ya nahi
if not all([GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY]):
    print("Error: Environment variables (GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY) nahi mile!")
    exit()

# Setup
genai.configure(api_key=GEMINI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def start_ingestion():
    print("Creating collection...")
    # Collection dobara banana
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )

    print("Fetching links...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_urls = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a', href=True) if '/docs/' in a['href']]
    all_urls = list(set(all_urls)) or [BASE_URL]

    point_id = 0
    for url in all_urls:
        print(f"Processing: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = soup.find('article') or soup.find('main')
        if not content: continue

        text = content.get_text(separator=' ', strip=True)
        # Create overlapping chunks to preserve context
        chunks = [text[i:i+1000] for i in range(0, len(text), 900)]

        points = []
        for chunk in chunks:
            result = genai.embed_content(model="models/text-embedding-004", content=chunk)
            points.append(PointStruct(
                id=point_id,
                vector=result['embedding'],
                payload={
                    "chunk_text": chunk,
                    "source": url,
                    "book_id": "textbook-1",
                    "chunk_index": point_id
                }
            ))
            point_id += 1

        if points:
            qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        time.sleep(1)  # Rate limiting to avoid API limits

    print(f"✅ SUCCESS: Total {point_id} points upload ho gaye to collection '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    start_ingestion()