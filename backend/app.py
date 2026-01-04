import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 1. Environment variables load karein (.env file se)
load_dotenv()

# 2. Path Fix: Python ko batayein ke 'src' folder kahan hai
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 3. Imports (Inhein try-except se bahar rakhein taaki error saaf dikhe)
try:
    from src.services.rag_service import load_textbook_content_from_docs
    from src.api.routers import api_router
    from src.auth.routes import router as auth_router
except ImportError as e:
    print(f"Critical Import Error: {e}")
    # Is point par agar error aaye toh check karein __init__.py files hain ya nahi

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    print("Loading textbook content into RAG system...")
    try:
        load_textbook_content_from_docs()
        print("Textbook content loaded successfully!")
    except Exception as e:
        print(f"RAG Loading Failed: {e}")

    yield
    # Shutdown Logic
    print("Shutting down server...")

# 4. FastAPI App Initialization
app = FastAPI(
    title=os.getenv("API_TITLE", "Textbook Generation API"),
    description=os.getenv("API_DESCRIPTION", "API for generating textbooks using AI"),
    version=os.getenv("API_VERSION", "1.0.0"),
    lifespan=lifespan
)

# 5. CORS Middleware (Hugging Face aur Localhost ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Include Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/auth") # Prefix add karna behtar hai

@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to Textbook Generation API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

# 7. Run Server
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # 'app:app' ki jagah direct 'app' object use karein reload=False mein
    uvicorn.run(app, host="0.0.0.0", port=port)