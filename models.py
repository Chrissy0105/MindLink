from extensions import db, bcrypt
from datetime import datetime
from random import SystemRandom
import string

# ---------------- Utility Functions ----------------

def generate_unique_username(length=8):
    chars = string.ascii_letters + string.digits
    for _ in range(1000):
        username = ''.join(SystemRandom().choices(chars, k=length))
        if not User.query.filter_by(username=username).first():
            return username
    raise Exception("Failed to generate unique username after 1000 attempts")

# ---------------- Models ----------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)  # Auto-increment primary key
    username = db.Column(db.String(50), unique=True, nullable=False, default=generate_unique_username)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)  # Mandatory telephone
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chats = db.relationship('ChatLog', backref='user', lazy=True)
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class ChatLog(db.Model):
    __tablename__ = "chat_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    risk_level = db.Column(db.Enum('low', 'medium', 'high', name='risk_level_enum'), nullable=False, default='low')

    def __repr__(self):
        return f"<ChatLog {self.id} - user {self.user_id}>"
