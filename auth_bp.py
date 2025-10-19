from flask import Blueprint, request, jsonify
from models import User
from extensions import db, bcrypt
import jwt
from config import Config
from datetime import datetime, timedelta

auth_bp = Blueprint('auth_bp', __name__) # Blueprint for auth routes

#------------------------- Sign Up Route -------------------------
@auth_bp.route('/signup', methods=['POST'])

def signup():
    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({'Error': 'Password is required'}) , 400
    
    # Creating new users (Username is generated automatically)
    user = User()
    user.email = data.get('email')
    user.set_password(data['password'])
    user.telephone = data.get('telephone', '')

    # Attempting to add user to the database
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Registration error:', str(e))  # Log the error to the server console
        return jsonify({'Error': f'Registration failed: {str(e)}'}), 400

    # Generate token for new user
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        },
        Config.JWT_SECRET_KEY,
        algorithm='HS256'
    )

    # Successful registration
    return jsonify({
        'message': 'User registered successfully',
        'username': user.username,
        'id': user.id,
        'token': token
    }), 201

#------------------------- Login Route -------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'Error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'Error': 'Invalid email or password'}), 401

    # Generate token
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
    })
    
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'Error': 'Invalid email or password'}), 401
    
    # Only verify telephone if provided during login
    if telephone and telephone != user.telephone:
        return jsonify({'Error': 'Telephone number does not match'}), 401
    
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=10) 
        }, 
        Config.JWT_SECRET_KEY,
        algorithm='HS256'
    )
    
    return jsonify({
        'message': 'Login Successful',
        'access_token': token,  # Changed from 'token' to 'access_token'
        'username': user.username,
        'telephone': user.telephone
    }), 200