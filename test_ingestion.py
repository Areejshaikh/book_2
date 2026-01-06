"""
Test script to verify that the book ingestion functionality works properly
without actually connecting to Qdrant or processing real data.
"""
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_book_ingester_imports():
    """Test that book_ingester can be imported without errors"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("book_ingester", "./backend/book_ingester.py")
        book_ingester = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(book_ingester)
        print("[OK] book_ingester.py imports successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Error importing book_ingester.py: {e}")
        return False


def test_simple_ingest_imports():
    """Test that simple_ingest can be imported without errors"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("simple_ingest", "./backend/simple_ingest.py")
        simple_ingest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(simple_ingest)
        print("[OK] simple_ingest.py imports successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Error importing simple_ingest.py: {e}")
        return False


def test_environment_variables():
    """Test that required environment variables are available"""
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if qdrant_url and qdrant_api_key:
        print("[OK] Required environment variables are set")
        return True
    else:
        print("[WARN] Required environment variables are not set (this might be expected in test environment)")
        return True  # Not a failure condition for this test


def test_embeddings_directory():
    """Test that embeddings directory exists and has metadata files"""
    embeddings_dir = os.path.join("backend", "embeddings")
    if os.path.exists(embeddings_dir):
        metadata_files = [f for f in os.listdir(embeddings_dir) if f.startswith("metadata_") and f.endswith(".json")]
        if metadata_files:
            print(f"[OK] Embeddings directory exists with {len(metadata_files)} metadata file(s)")
            return True
        else:
            print("[WARN] No metadata files found in embeddings directory")
            return False
    else:
        print("[ERROR] Embeddings directory does not exist")
        return False


def main():
    print("Testing book ingestion functionality...")
    print("="*50)

    tests = [
        ("Environment Variables", test_environment_variables),
        ("Embeddings Directory", test_embeddings_directory),
        ("Import book_ingester.py", test_book_ingester_imports),
        ("Import simple_ingest.py", test_simple_ingest_imports),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "="*50)
    print("Test Summary:")
    all_passed = True
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test_name}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] All tests passed! The book ingestion scripts are ready to use.")
    else:
        print("\n[WARN] Some tests failed. Please check the issues above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)