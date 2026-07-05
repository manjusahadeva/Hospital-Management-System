from database import DBConnection
from models.user import User
from utils.helpers import hash_password
class AuthService:
    """
    Handles user authentication, login checks, and account registration.
    """
    @staticmethod
    def login(username, password):
        """
        Authenticates username and password against database.
        Returns User object on success, or None on failure.
        """
        hashed = hash_password(password)
        try:
            with DBConnection() as (conn, cursor):
                query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
                cursor.execute(query, (username, hashed))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        password_hash=row['password_hash'],
                        role=row['role'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            print(f"[Auth Error] Failed to login user: {e}")
        return None
    @staticmethod
    def create_user(username, password, role):
        """
        Registers a new user inside the database.
        Returns the user_id of the created user, or None on failure.
        """
        hashed = hash_password(password)
        try:
            with DBConnection() as (conn, cursor):
                # Check if username exists
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print(f"[Registration Error] Username '{username}' already exists.")
                    return None
                
                query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, hashed, role))
                # Connection commits automatically on exit if no error
                return cursor.lastrowid
        except Exception as e:
            print(f"[Registration Error] Failed to create user: {e}")
            return None
