import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    print("Testing endpoints...")
    
    # Test health
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code} - {response.json()}")
    
    # Test registration
    reg_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "telephone": "18761234567"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        print(f"Register: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Register failed: {e}")
    
    # Test login
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"Token: {token[:50]}...")
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    test_endpoints()
