"""
Simple test script to verify backend authentication works.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    data = {
        "email": "test123@example.com",
        "password": "password123",
        "name": "Test User"
    }
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_login(email, password):
    """Test user login"""
    print("Testing user login...")
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

if __name__ == "__main__":
    # Test health
    test_health()

    # Test registration
    register_result = test_register()

    # Test login (only if registration succeeded)
    if "token" in register_result:
        test_login("test123@example.com", "password123")
