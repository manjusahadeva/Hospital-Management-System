class Doctor:
    def __init__(self, name, specialization, phone, email=None, qualification=None, user_id=None, doctor_id=None, created_at=None):
        self.doctor_id = doctor_id  # Unique string identifier, e.g., DOC-10001
        self.user_id = user_id  # Links to user credentials in 'users' table
        self.name = name
        self.specialization = specialization
        self.phone = phone
        self.email = email
        self.qualification = qualification
        self.created_at = created_at
    def __repr__(self):
        return f"Doctor(id='{self.doctor_id}', name='{self.name}', spec='{self.specialization}')"