import requests

def test_health():
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"✅ Health: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return False

def test_endpoint(url, method="GET", data=None):
    try:
        if method == "POST":
            response = requests.post(url, json=data or {})
        else:
            response = requests.get(url)
        print(f"📍 {method} {url}: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text[:100]}...")
        return response.status_code
    except Exception as e:
        print(f"❌ {method} {url} failed: {e}")
        return None

if __name__ == "__main__":
    print("Testing endpoints...")
    test_health()
    
    endpoints = [
        ("/auth/register", "POST", {"test": "data"}),
        ("/auth/login", "POST", {"test": "data"}),
        ("/auth/signup", "POST", {"test": "data"}),
        ("/auth/signin", "POST", {"test": "data"}),
        ("/register", "POST", {"test": "data"}),
        ("/login", "POST", {"test": "data"}),
    ]
    
    for endpoint, method, data in endpoints:
        test_endpoint(f"http://localhost:5000{endpoint}", method, data)
