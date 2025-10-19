from flask import Blueprint, request, jsonify
from models import User
from extensions import db, bcrypt
import jwt
from config import Config
from datetime import datetime, timedelta

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'Error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        telephone = data.get('telephone', '')
        
        if not email or not password:
            return jsonify({'Error': 'Email and password are required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'Error': 'Email already exists'}), 400
        
        # Create new user
        user = User()
        user.email = email
        user.set_password(password)
        user.telephone = telephone

        # Save to database
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        return jsonify({
            'message': 'User registered successfully',
            'username': user.username,
            'id': user.id,
            'token': token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'Error': f'Registration failed: {str(e)}'}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'Error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'Error': 'Email and password are required'}), 400

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'Error': 'Invalid email or password'}), 401

        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        return jsonify({
            'message': 'Login successful',
            'username': user.username,
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'Error': f'Login failed: {str(e)}'}), 400