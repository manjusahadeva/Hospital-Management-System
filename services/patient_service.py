from database import DBConnection
from models.patient import Patient
from utils.helpers import generate_unique_id
from utils.validators import validate_date, validate_phone, validate_email, validate_gender
class PatientService:
    """
    Business Logic Layer for Patient Management.
    Performs validation and handles data operations with DB.
    """
    @staticmethod
    def add_patient(name, dob, gender, phone, email=None, address=None):
        """
        Validates data and creates a new patient record with a generated unique ID.
        """
        # Validate inputs
        if not name.strip():
            print("[Validation Error] Name cannot be empty.")
            return None
        if not validate_date(dob):
            print("[Validation Error] Invalid Date of Birth format. Use YYYY-MM-DD.")
            return None
        if not validate_gender(gender):
            print("[Validation Error] Invalid Gender. Choose Male, Female, or Other.")
            return None
        if not validate_phone(phone):
            print("[Validation Error] Invalid Phone Number. Must contain 10-15 digits.")
            return None
        if email and not validate_email(email):
            print("[Validation Error] Invalid Email format.")
            return None
        try:
            with DBConnection() as (conn, cursor):
                # Generate unique formatted ID
                patient_id = generate_unique_id("PAT", "patients", "patient_id", cursor)
                
                query = """
                    INSERT INTO patients (patient_id, name, dob, gender, phone, email, address)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (patient_id, name.strip(), dob, gender.title(), phone, email, address))
                print(f"\n[Success] Patient added successfully! ID: {patient_id}")
                return patient_id
        except Exception as e:
            print(f"\n[Database Error] Failed to add patient: {e}")
            return None
    @staticmethod
    def update_patient(patient_id, name=None, dob=None, gender=None, phone=None, email=None, address=None):
        """
        Updates patient details based on ID. Only non-empty parameters are updated.
        """
        # First check if patient exists
        patient = PatientService.get_patient_by_id(patient_id)
        if not patient:
            print(f"[Error] Patient with ID '{patient_id}' not found.")
            return False
        # Build query dynamically based on provided fields
        fields = []
        values = []
        if name and name.strip():
            fields.append("name = %s")
            values.append(name.strip())
        if dob:
            if not validate_date(dob):
                print("[Validation Error] Invalid Date of Birth format. Use YYYY-MM-DD.")
                return False
            fields.append("dob = %s")
            values.append(dob)
        if gender:
            if not validate_gender(gender):
                print("[Validation Error] Invalid Gender. Choose Male, Female, or Other.")
                return False
            fields.append("gender = %s")
            values.append(gender.title())
        if phone:
            if not validate_phone(phone):
                print("[Validation Error] Invalid Phone. Must contain 10-15 digits.")
                return False
            fields.append("phone = %s")
            values.append(phone)
        if email is not None:
            if email and not validate_email(email):
                print("[Validation Error] Invalid Email format.")
                return False
            fields.append("email = %s")
            values.append(email if email else None)
        if address is not None:
            fields.append("address = %s")
            values.append(address if address else None)
        if not fields:
            print("[Warning] No update fields provided.")
            return False
        values.append(patient_id)
        query = f"UPDATE patients SET {', '.join(fields)} WHERE patient_id = %s"
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute(query, tuple(values))
                print(f"\n[Success] Patient '{patient_id}' updated successfully.")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to update patient: {e}")
            return False
    @staticmethod
    def delete_patient(patient_id):
        """
        Deletes a patient by their unique ID.
        """
        patient = PatientService.get_patient_by_id(patient_id)
        if not patient:
            print(f"[Error] Patient with ID '{patient_id}' not found.")
            return False
        try:
            with DBConnection() as (conn, cursor):
                query = "DELETE FROM patients WHERE patient_id = %s"
                cursor.execute(query, (patient_id,))
                print(f"\n[Success] Patient '{patient_id}' deleted successfully.")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to delete patient: {e}")
            return False
    @staticmethod
    def search_patients(search_term):
        """
        Searches patients by ID, Name, or Phone. Supports partial matching for names.
        """
        results = []
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT * FROM patients 
                    WHERE patient_id = %s 
                       OR phone = %s 
                       OR name LIKE %s
                """
                like_term = f"%{search_term}%"
                cursor.execute(query, (search_term, search_term, like_term))
                rows = cursor.fetchall()
                for row in rows:
                    results.append(
                        Patient(
                            patient_id=row['patient_id'],
                            name=row['name'],
                            dob=str(row['dob']),
                            gender=row['gender'],
                            phone=row['phone'],
                            email=row['email'],
                            address=row['address'],
                            created_at=row['created_at']
                        )
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to search patients: {e}")
        return results
    @staticmethod
    def get_all_patients():
        """
        Retrieves all patient records from the database.
        """
        patients = []
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
                rows = cursor.fetchall()
                for row in rows:
                    patients.append(
                        Patient(
                            patient_id=row['patient_id'],
                            name=row['name'],
                            dob=str(row['dob']),
                            gender=row['gender'],
                            phone=row['phone'],
                            email=row['email'],
                            address=row['address'],
                            created_at=row['created_at']
                        )
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch patients: {e}")
        return patients
    @staticmethod
    def get_patient_by_id(patient_id):
        """
        Fetches a single patient record by its primary key ID.
        """
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
                row = cursor.fetchone()
                if row:
                    return Patient(
                        patient_id=row['patient_id'],
                        name=row['name'],
                        dob=str(row['dob']),
                        gender=row['gender'],
                        phone=row['phone'],
                        email=row['email'],
                        address=row['address'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch patient: {e}")
        return None
