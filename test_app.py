# test_flask_routes.py
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import app
from extensions import db, bcrypt
from models import User
import jwt
from datetime import datetime, timedelta

# -------------------------- Pytest fixtures --------------------------
@pytest.fixture
def client():
    """Flask test client with test database."""
    # Use test configuration
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-testing'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Create a test user
            test_user = User()
            test_user.username="testuser123",
            test_user.email="test@example.com", 
            test_user.telephone="1234567890"
            
            test_user.set_password("testpassword")
            db.session.add(test_user)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Generate JWT token for authenticated requests."""
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        if user is None:
            raise RuntimeError("Test user not found in database. Ensure test user is created in the fixture.")
        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm="HS256")
        return {'Authorization': f'Bearer {token}'}

# -------------------------- Flask Route Tests --------------------------

def test_health_check(client):
    """Test health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'

def test_high_risk_message(client, auth_headers):
    """Test high risk message detection."""
    user_message = {"message": "I don't want to be here anymore. I want to end my life."}

    response = client.post('/chat/message', json=user_message, headers=auth_headers)
    print("High risk test working...")
    assert response.status_code == 201

    data = response.get_json()
    assert data["risk_level"] == "high"
    assert "alert" in data
    assert "helplines" in data
    assert "SafeSpot JA" in data["helplines"]
    print("High risk detection successful!")

def test_medium_risk_message(client, auth_headers):
    """Test medium risk message detection."""
    user_message = {"message": "I've been feeling really sad and hopeless lately."}

    response = client.post('/chat/message', json=user_message, headers=auth_headers)
    assert response.status_code == 201

    data = response.get_json()
    assert data["risk_level"] == "medium"
    assert "alert" not in data

def test_low_risk_message(client, auth_headers):
    """Test low risk message detection."""
    user_message = {"message": "I am feeling great today!"}

    response = client.post('/chat/message', json=user_message, headers=auth_headers)
    assert response.status_code == 201

    data = response.get_json()
    assert data["risk_level"] == "low"
    assert "alert" not in data

def test_empty_message(client, auth_headers):
    """Test sending empty message."""
    user_message = {"message": ""}
    
    response = client.post('/chat/message', json=user_message, headers=auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_chat_history(client, auth_headers):
    """Test retrieving chat history."""
    # First send a message
    user_message = {"message": "Test message for history"}
    response = client.post('/chat/message', json=user_message, headers=auth_headers)
    assert response.status_code == 201
    
    # Then get history
    response = client.get('/chat/history', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'chats' in data
    assert len(data['chats']) == 1
    assert data['chats'][0]['message'] == "Test message for history"

def test_unauthorized_access(client):
    """Test accessing protected routes without token."""
    response = client.post('/chat/message', json={"message": "test"})
    assert response.status_code == 401
    
    response = client.get('/chat/history')
    assert response.status_code == 401

def test_invalid_token(client):
    """Test accessing protected routes with invalid token."""
    headers = {'Authorization': 'Bearer invalid-token-here'}
    response = client.post('/chat/message', json={"message": "test"}, headers=headers)
    assert response.status_code == 401