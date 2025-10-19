import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth_flow():
    print("🔐 Testing Authentication Flow")
    print("=" * 40)
    
    # Generate unique test data
    import random
    random_id = random.randint(1000, 9999)
    test_email = f"test{random_id}@example.com"
    
    test_user = {
        "email": test_email,
        "password": "TestPass123!",
        "telephone": "1876" + str(random.randint(1000000, 9999999))
    }
    
    print(f"Test user: {test_user['email']}")
    
    # 1. Test Signup
    print("\n1. Testing Signup...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/signup", json=test_user)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 201:
            print("   ✅ Signup Successful!")
            print(f"   Response: {json.dumps(resp.json(), indent=4)}")
        else:
            print(f"   Response: {resp.text}")
    except Exception as e:
        print(f"   ❌ Signup error: {e}")
        return None
    
    # 2. Test Login
    print("\n2. Testing Login...")
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            token = resp.json().get('access_token')
            if token:
                print("   ✅ Login Successful!")
                print(f"   Token: {token[:50]}...")
                return token
            else:
                print("   ❌ No token in response")
                print(f"   Response: {json.dumps(resp.json(), indent=4)}")
        else:
            print(f"   Response: {resp.text}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    return None

def test_chat_with_token(token):
    if not token:
        print("\n❌ No token - skipping chat tests")
        return
    
    print("\n3. Testing Chat Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_messages = [
        {"message": "I am feeling great today!", "expected_risk": "low"},
        {"message": "I feel a bit sad and lonely lately", "expected_risk": "medium"},
        {"message": "I don't want to live anymore", "expected_risk": "high"}
    ]
    
    for test in test_messages:
        print(f"\n   Testing: '{test['message']}'")
        try:
            resp = requests.post(
                f"{BASE_URL}/chat/message",
                json={"message": test["message"]},
                headers=headers
            )
            print(f"   Status: {resp.status_code}")
            if resp.status_code == 201:
                data = resp.json()
                print(f"   ✅ Risk Level: {data['risk_level']} (expected: {test['expected_risk']})")
                if data.get('alert'):
                    print(f"   🚨 ALERT: {data['alert']}")
            else:
                print(f"   Response: {resp.text}")
        except Exception as e:
            print(f"   ❌ Chat error: {e}")

if __name__ == "__main__":
    token = test_auth_flow()
    test_chat_with_token(token)
    print("\n🎉 Testing Complete!")
