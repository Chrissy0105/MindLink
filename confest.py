import pytest
from app import app as flask_app
from models import db

@pytest.fixture
def app():
    # Use test config if you have one
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
