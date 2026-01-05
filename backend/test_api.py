"""
Test script to verify API endpoints are working correctly
"""
import requests
import json

# Base URL for the API (adjust as needed)


def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")

def test_api_health():
    """Test the API health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"API health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error testing API health endpoint: {e}")

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        # This is a POST request, so we need to send data
        headers = {"Content-Type": "application/json"}
        data = {
            "query": "What is AI?",
            "book_id": "test_book",
            "session_id": "test_session"
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat", headers=headers, json=data)
        print(f"Chat endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing chat endpoint: {e}")

def test_corrected_chat_endpoint():
    """Test the corrected chat endpoint (without double prefix)"""
    try:
        # This is a POST request, so we need to send data
        headers = {"Content-Type": "application/json"}
        data = {
            "query": "What is AI?",
            "book_id": "test_book",
            "session_id": "test_session"
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat", headers=headers, json=data)
        print(f"Corrected chat endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing corrected chat endpoint: {e}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_health_endpoint()
    test_api_health()
    test_chat_endpoint()  # This will likely fail due to double prefix
    test_corrected_chat_endpoint()  # This should work with the fix