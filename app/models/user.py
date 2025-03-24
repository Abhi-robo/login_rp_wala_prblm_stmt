from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.services.database_service import get_user_by_id, get_user_by_email, create_user as db_create_user

class User(UserMixin):
    def __init__(self, id, email, password_hash, name, created_at):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.created_at = created_at

    @staticmethod
    def get_by_id(user_id):
        user_data = get_user_by_id(user_id)
        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                name=user_data['name'],
                created_at=user_data['created_at']
            )
        return None

    @staticmethod
    def get_by_email(email):
        user_data = get_user_by_email(email)
        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                name=user_data['name'],
                created_at=user_data['created_at']
            )
        return None

    @staticmethod
    def create_user(email, password, name):
        password_hash = generate_password_hash(password)
        user_id = db_create_user(email, password_hash, name)
        user_data = get_user_by_id(user_id)
        
        return User(
            id=user_data['id'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            name=user_data['name'],
            created_at=user_data['created_at']
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) 