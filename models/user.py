class User:
    def __init__(self, username, password_hash, role, user_id=None, created_at=None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # Admin, Doctor, Receptionist
        self.created_at = created_at
    def __repr__(self):
        return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"
