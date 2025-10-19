import requests
import json
import random

BASE_URL = "http://localhost:5000"

def test_complete_flow():
    print("🚀 Testing Complete Authentication & Risk Detection Flow")
    print("=" * 60)
    
    # Generate unique test data
    random_id = random.randint(1000, 9999)
    test_email = f"finaltest{random_id}@example.com"
    test_telephone = "1876" + str(random.randint(1000000, 9999999))
    
    test_user = {
        "email": test_email,
        "password": "TestPass123!",
        "telephone": test_telephone
    }
    
    print(f"Test User: {test_email}")
    print(f"Test Telephone: {test_telephone}")
    
    # 1. Signup
    print("\n1. 📝 Signup...")
    signup_resp = requests.post(f"{BASE_URL}/auth/signup", json=test_user)
    if signup_resp.status_code == 201:
        print("   ✅ Signup Successful!")
        print(f"   {signup_resp.json()}")
    else:
        print(f"   ❌ Signup Failed: {signup_resp.text}")
        return
    
    # 2. Login
    print("\n2. 🔑 Login...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json=test_user)
    if login_resp.status_code == 200:
        token = login_resp.json().get('token')
        if token:
            print("   ✅ Login Successful!")
            print(f"   Token received: {token[:50]}...")
        else:
            print("   ❌ No token in response")
            return
    else:
        print(f"   ❌ Login Failed: {login_resp.text}")
        return
    
    # 3. Test All Risk Levels
    print("\n3. 💬 Testing All Risk Levels...")
    headers = {"Authorization": f"Bearer {token}"}
    
    risk_tests = [
        {
            "message": "I am feeling great and happy today!",
            "expected": "low",
            "description": "LOW RISK - Positive mood"
        },
        {
            "message": "I've been feeling sad and stressed lately",
            "expected": "medium", 
            "description": "MEDIUM RISK - Depressive symptoms"
        },
        {
            "message": "I don't want to live anymore",
            "expected": "high",
            "description": "HIGH RISK - Suicidal ideation"
        },
        {
            "message": "I want to end my life",
            "expected": "high",
            "description": "HIGH RISK - Direct suicide threat"
        }
    ]
    
    for test in risk_tests:
        print(f"\n   Testing: {test['description']}")
        print(f"   Message: '{test['message']}'")
        
        chat_resp = requests.post(
            f"{BASE_URL}/chat/message",
            json={"message": test["message"]},
            headers=headers
        )
        
        if chat_resp.status_code == 201:
            data = chat_resp.json()
            actual_risk = data['risk_level']
            status = "✅" if actual_risk == test['expected'] else "❌"
            
            print(f"   {status} Risk Level: {actual_risk} (expected: {test['expected']})")
            
            if actual_risk == 'high':
                print(f"   🚨 EMERGENCY ALERT: {data.get('alert', 'No alert')}")
                if data.get('helplines'):
                    print(f"   📞 HELPLINES ACTIVATED")
        else:
            print(f"   ❌ Chat Failed: {chat_resp.text}")
    
    print("\n🎉 TESTING COMPLETE!")
    print("All risk levels should now be detected correctly.")

if __name__ == "__main__":
    test_complete_flow()
