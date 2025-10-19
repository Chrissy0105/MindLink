#!/bin/bash

echo "🚀 Complete Authentication & Chat Test"

# Generate unique test data
RANDOM_ID=$(( RANDOM % 10000 ))
TEST_EMAIL="finaltest${RANDOM_ID}@example.com"
TEST_PASSWORD="FinalPass123!"
TEST_PHONE="1876$(( RANDOM % 10000000 ))"

echo "Test User: $TEST_EMAIL"
echo "Test Phone: $TEST_PHONE"

echo -e "\n1. 📝 Signup..."
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"telephone\": \"$TEST_PHONE\"
  }")

echo "$SIGNUP_RESPONSE" | python3 -m json.tool

echo -e "\n2. 🔑 Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"telephone\": \"$TEST_PHONE\"
  }")

echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extract token correctly (it's "token" field)
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', 'NO_TOKEN'))")

if [ "$TOKEN" != "NO_TOKEN" ]; then
    echo -e "\n3. 💬 Testing Chat with Different Risk Levels..."
    
    echo -e "\n   Testing LOW risk..."
    curl -s -X POST http://localhost:5000/chat/message \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"message": "I am feeling great and happy today!"}' | python3 -m json.tool
    
    echo -e "\n   Testing MEDIUM risk..."
    curl -s -X POST http://localhost:5000/chat/message \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"message": "I feel sad and stressed lately"}' | python3 -m json.tool
    
    echo -e "\n   Testing HIGH risk..."
    curl -s -X POST http://localhost:5000/chat/message \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"message": "I want to end my life"}' | python3 -m json.tool
    
    echo -e "\n4. 📜 Testing Chat History..."
    curl -s -X GET http://localhost:5000/chat/history \
      -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
else
    echo -e "\n❌ No token received"
fi

echo -e "\n✅ All Tests Complete!"
