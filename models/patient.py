class Patient:
    def __init__(self, name, dob, gender, phone, email=None, address=None, patient_id=None, created_at=None):
        self.patient_id = patient_id  # Unique string identifier, e.g., PAT-10001
        self.name = name
        self.dob = dob  # Date of birth (YYYY-MM-DD)
        self.gender = gender  # Male, Female, Other
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at
    def __repr__(self):
        return f"Patient(id='{self.patient_id}', name='{self.name}', phone='{self.phone}')"
