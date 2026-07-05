import unittest
import sys
import os
# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.validators import validate_date, validate_time, validate_phone, validate_email
from utils.helpers import hash_password
from models.user import User
from models.patient import Patient
class TestHospitalManagementSystem(unittest.TestCase):
    """
    Unit test cases for the helper validation functions, cryptography,
    and object-oriented data models.
    """
    
    def test_validators(self):
        # 1. Date Validation (YYYY-MM-DD)
        self.assertTrue(validate_date("2026-07-04"))
        self.assertFalse(validate_date("04-07-2026"))
        self.assertFalse(validate_date("2026-13-45"))  # Invalid month/day
        
        # 2. Time Validation (HH:MM)
        self.assertTrue(validate_time("14:30"))
        self.assertFalse(validate_time("25:00"))  # Invalid hours
        self.assertFalse(validate_time("14:60"))  # Invalid minutes
        
        # 3. Phone Validation (10-15 digits)
        self.assertTrue(validate_phone("9876543210"))
        self.assertTrue(validate_phone("123456789012"))
        self.assertFalse(validate_phone("9876543"))     # Too short
        self.assertFalse(validate_phone("abc1234567"))  # Non-numeric
        
        # 4. Email Validation
        self.assertTrue(validate_email("test@hospital.com"))
        self.assertTrue(validate_email(None))  # Optional email is allowed
        self.assertFalse(validate_email("test@hospital"))  # Missing domain extension
    def test_password_hashing(self):
        # SHA-256 validation
        admin_hash = hash_password("admin123")
        self.assertEqual(len(admin_hash), 64)
        self.assertEqual(admin_hash, "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9")
    def test_models_creation(self):
        # OOP User Model
        user = User(username="receptionist", password_hash="dummyhash", role="Receptionist", user_id=2)
        self.assertEqual(user.username, "receptionist")
        self.assertEqual(user.role, "Receptionist")
        self.assertEqual(user.user_id, 2)
        
        # OOP Patient Model
        patient = Patient(name="Alice", dob="1995-10-12", gender="Female", phone="9988776655")
        self.assertEqual(patient.name, "Alice")
        self.assertEqual(patient.dob, "1995-10-12")
        self.assertEqual(patient.gender, "Female")
        self.assertEqual(patient.phone, "9988776655")
if __name__ == '__main__':
    unittest.main()
