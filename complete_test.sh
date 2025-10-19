#!/bin/bash

echo "🚀 Testing Mental Health App Authentication"

# Generate unique test data
RANDOM_ID=$(( RANDOM % 10000 ))
TEST_EMAIL="testuser${RANDOM_ID}@example.com"
TEST_PASSWORD="TestPass123!"
TEST_PHONE="1876$(( RANDOM % 10000000 ))"

echo "Test User: $TEST_EMAIL"

echo -e "\n1. Testing Signup..."
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\", 
    \"telephone\": \"$TEST_PHONE\"
  }")

echo "$SIGNUP_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SIGNUP_RESPONSE"

echo -e "\n2. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract token from login response
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo -e "\n3. Testing Chat with Token..."
    curl -X POST http://localhost:5000/chat/message \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"message": "I am feeling great!"}' | python3 -m json.tool
else
    echo -e "\n❌ No token received"
fi

echo -e "\n✅ Testing Complete!"
