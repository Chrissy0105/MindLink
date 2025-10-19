from app import app, db
from models import User

def setup_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

        # Create test user
        test_user = User()
        test_user.email = "test@example.com"
        test_user.set_password("testpassword123")
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully!")
            print("You can now log in with:")
            print("Email: test@example.com")
            print("Password: testpassword123")
        except Exception as e:
            db.session.rollback()
            print("Error creating test user:", str(e))

if __name__ == "__main__":
    setup_database()