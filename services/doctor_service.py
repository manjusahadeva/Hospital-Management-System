from database import DBConnection
from models.doctor import Doctor
from utils.helpers import generate_unique_id, hash_password
from utils.validators import validate_phone, validate_email
class DoctorService:
    """
    Business Logic Layer for Doctor Management.
    Includes transaction-safe creation linking doctors with users.
    """
    @staticmethod
    def add_doctor(name, specialization, phone, email, qualification, username, password):
        """
        Registers a new Doctor profile. This is transaction-safe.
        Creates a user account first, then links it to the Doctor profile.
        """
        # Validations
        if not name.strip() or not specialization.strip():
            print("[Validation Error] Name and Specialization cannot be empty.")
            return None
        if not validate_phone(phone):
            print("[Validation Error] Invalid Phone. Must contain 10-15 digits.")
            return None
        if email and not validate_email(email):
            print("[Validation Error] Invalid Email format.")
            return None
        if not username.strip() or not password.strip():
            print("[Validation Error] Username and Password are required for Doctor login account.")
            return None
        hashed = hash_password(password)
        try:
            with DBConnection() as (conn, cursor):
                # 1. Check if username already exists
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username.strip(),))
                if cursor.fetchone():
                    print(f"\n[Error] Username '{username}' already exists. Choose another.")
                    return None
                # 2. Insert user account
                user_query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'Doctor')"
                cursor.execute(user_query, (username.strip(), hashed))
                user_id = cursor.lastrowid
                # 3. Generate Doctor ID
                doctor_id = generate_unique_id("DOC", "doctors", "doctor_id", cursor)
                # 4. Insert doctor profile linked to user_id
                doc_query = """
                    INSERT INTO doctors (doctor_id, user_id, name, specialization, phone, email, qualification)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(doc_query, (
                    doctor_id, 
                    user_id, 
                    name.strip(), 
                    specialization.strip(), 
                    phone, 
                    email, 
                    qualification
                ))
                
                print(f"\n[Success] Doctor added successfully! ID: {doctor_id} | Username: {username}")
                return doctor_id
        except Exception as e:
            print(f"\n[Database Transaction Error] Failed to create doctor account: {e}")
            return None
    @staticmethod
    def update_doctor(doctor_id, name=None, specialization=None, phone=None, email=None, qualification=None):
        """
        Updates doctor profile parameters.
        """
        doctor = DoctorService.get_doctor_by_id(doctor_id)
        if not doctor:
            print(f"[Error] Doctor with ID '{doctor_id}' not found.")
            return False
        fields = []
        values = []
        if name and name.strip():
            fields.append("name = %s")
            values.append(name.strip())
        if specialization and specialization.strip():
            fields.append("specialization = %s")
            values.append(specialization.strip())
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
        if qualification is not None:
            fields.append("qualification = %s")
            values.append(qualification if qualification else None)
        if not fields:
            print("[Warning] No update fields provided.")
            return False
        values.append(doctor_id)
        query = f"UPDATE doctors SET {', '.join(fields)} WHERE doctor_id = %s"
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute(query, tuple(values))
                print(f"\n[Success] Doctor '{doctor_id}' updated successfully.")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to update doctor: {e}")
            return False
    @staticmethod
    def delete_doctor(doctor_id):
        """
        Deletes doctor profile and the associated user account.
        Uses a transaction to ensure both records are removed or none.
        """
        doctor = DoctorService.get_doctor_by_id(doctor_id)
        if not doctor:
            print(f"[Error] Doctor with ID '{doctor_id}' not found.")
            return False
        try:
            with DBConnection() as (conn, cursor):
                # Fetch user_id to delete from users table
                cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = %s", (doctor_id,))
                row = cursor.fetchone()
                user_id = row['user_id'] if row else None
                # 1. Delete doctor profile (foreign keys set to cascade/null as needed)
                cursor.execute("DELETE FROM doctors WHERE doctor_id = %s", (doctor_id,))
                # 2. Delete linked user account
                if user_id:
                    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                
                print(f"\n[Success] Doctor '{doctor_id}' and linked user account deleted successfully.")
                return True
        except Exception as e:
            print(f"\n[Database Transaction Error] Failed to delete doctor: {e}")
            return False
    @staticmethod
    def search_doctors(search_term):
        """
        Searches doctors by ID, Name, Specialization, or Phone.
        """
        results = []
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT * FROM doctors 
                    WHERE doctor_id = %s 
                       OR phone = %s 
                       OR name LIKE %s 
                       OR specialization LIKE %s
                """
                like_term = f"%{search_term}%"
                cursor.execute(query, (search_term, search_term, like_term, like_term))
                rows = cursor.fetchall()
                for row in rows:
                    results.append(
                        Doctor(
                            doctor_id=row['doctor_id'],
                            user_id=row['user_id'],
                            name=row['name'],
                            specialization=row['specialization'],
                            phone=row['phone'],
                            email=row['email'],
                            qualification=row['qualification'],
                            created_at=row['created_at']
                        )
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to search doctors: {e}")
        return results
    @staticmethod
    def get_all_doctors():
        """
        Retrieves all doctor records.
        """
        doctors = []
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT * FROM doctors ORDER BY created_at DESC")
                rows = cursor.fetchall()
                for row in rows:
                    doctors.append(
                        Doctor(
                            doctor_id=row['doctor_id'],
                            user_id=row['user_id'],
                            name=row['name'],
                            specialization=row['specialization'],
                            phone=row['phone'],
                            email=row['email'],
                            qualification=row['qualification'],
                            created_at=row['created_at']
                        )
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch doctors: {e}")
        return doctors
    @staticmethod
    def get_doctor_by_id(doctor_id):
        """
        Fetches a doctor profile by doctor_id.
        """
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
                row = cursor.fetchone()
                if row:
                    return Doctor(
                        doctor_id=row['doctor_id'],
                        user_id=row['user_id'],
                        name=row['name'],
                        specialization=row['specialization'],
                        phone=row['phone'],
                        email=row['email'],
                        qualification=row['qualification'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch doctor: {e}")
        return None
    @staticmethod
    def get_doctor_by_user_id(user_id):
        """
        Fetches a doctor profile associated with a user account ID.
        Useful when a doctor logs in and wants to see their schedule.
        """
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT * FROM doctors WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                if row:
                    return Doctor(
                        doctor_id=row['doctor_id'],
                        user_id=row['user_id'],
                        name=row['name'],
                        specialization=row['specialization'],
                        phone=row['phone'],
                        email=row['email'],
                        qualification=row['qualification'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch doctor by user ID: {e}")
        return None
