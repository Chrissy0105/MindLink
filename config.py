import os 
from dotenv import load_dotenv
from datetime import timedelta

# ----------------------- Loading Environment ---------------------------
load_dotenv()

class Config:
    # Flask secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Default JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', default='jwt-secret-key')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mental_health.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False      # To suppress warning

    # jwt expiration time, default 2 hours
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 5))) 

    # debug mode
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)  # Shorter expiration for testin