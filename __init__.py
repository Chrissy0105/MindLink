# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load config from config.py
    app.config.from_object("config.Config")

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    
    from .models import User, ChatLog  # Import models to register them with SQLAlchemy
    return app
