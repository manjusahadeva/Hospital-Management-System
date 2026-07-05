from database import DBConnection
from models.appointment import Appointment
from utils.helpers import generate_unique_id
from utils.validators import validate_date, validate_time
from services.patient_service import PatientService
from services.doctor_service import DoctorService
class AppointmentService:
    """
    Business Logic Layer for Appointment Management.
    Enforces double-booking prevention and referential integrity checks.
    """
    @staticmethod
    def book_appointment(patient_id, doctor_id, appointment_date, appointment_time, reason=None):
        """
        Books a new appointment.
        Validates date/time, checks references, and prevents double-booking.
        """
        # Validate date and time format
        if not validate_date(appointment_date):
            print("[Validation Error] Invalid Appointment Date. Use YYYY-MM-DD.")
            return None
        if not validate_time(appointment_time):
            print("[Validation Error] Invalid Appointment Time. Use HH:MM.")
            return None
        # Verify Patient and Doctor exist
        patient = PatientService.get_patient_by_id(patient_id)
        if not patient:
            print(f"[Error] Patient with ID '{patient_id}' does not exist.")
            return None
        doctor = DoctorService.get_doctor_by_id(doctor_id)
        if not doctor:
            print(f"[Error] Doctor with ID '{doctor_id}' does not exist.")
            return None
        try:
            with DBConnection() as (conn, cursor):
                # Check for double booking (Same doctor, same date, same time, status is not Cancelled)
                check_query = """
                    SELECT appointment_id FROM appointments 
                    WHERE doctor_id = %s 
                      AND appointment_date = %s 
                      AND appointment_time = %s 
                      AND status != 'Cancelled'
                """
                cursor.execute(check_query, (doctor_id, appointment_date, appointment_time))
                if cursor.fetchone():
                    print(f"\n[Scheduling Conflict] Dr. {doctor.name} is already booked at {appointment_time} on {appointment_date}.")
                    return None
                # Generate Unique ID
                appointment_id = generate_unique_id("APT", "appointments", "appointment_id", cursor)
                # Insert appointment record
                query = """
                    INSERT INTO appointments (appointment_id, patient_id, doctor_id, appointment_date, appointment_time, reason, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
                """
                cursor.execute(query, (
                    appointment_id, 
                    patient_id, 
                    doctor_id, 
                    appointment_date, 
                    appointment_time, 
                    reason
                ))
                
                print(f"\n[Success] Appointment booked successfully! ID: {appointment_id}")
                return appointment_id
        except Exception as e:
            print(f"\n[Database Error] Failed to book appointment: {e}")
            return None
    @staticmethod
    def cancel_appointment(appointment_id):
        """
        Cancels an appointment by setting its status to 'Cancelled'.
        """
        try:
            with DBConnection() as (conn, cursor):
                # Check if exists
                cursor.execute("SELECT status FROM appointments WHERE appointment_id = %s", (appointment_id,))
                row = cursor.fetchone()
                if not row:
                    print(f"[Error] Appointment with ID '{appointment_id}' not found.")
                    return False
                
                if row['status'] == 'Cancelled':
                    print("[Warning] Appointment is already cancelled.")
                    return True
                
                # Perform cancellation
                cursor.execute("UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s", (appointment_id,))
                print(f"\n[Success] Appointment '{appointment_id}' has been cancelled.")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to cancel appointment: {e}")
            return False
    @staticmethod
    def complete_appointment(appointment_id):
        """
        Marks an appointment as completed.
        """
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT status FROM appointments WHERE appointment_id = %s", (appointment_id,))
                row = cursor.fetchone()
                if not row:
                    print(f"[Error] Appointment with ID '{appointment_id}' not found.")
                    return False
                
                cursor.execute("UPDATE appointments SET status = 'Completed' WHERE appointment_id = %s", (appointment_id,))
                print(f"\n[Success] Appointment '{appointment_id}' marked as Completed.")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to complete appointment: {e}")
            return False
    @staticmethod
    def get_appointments(doctor_id=None, patient_id=None):
        """
        Retrieves appointments, optionally filtering by doctor or patient.
        Joins with patients and doctors tables for friendly names.
        """
        results = []
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT a.*, p.name AS patient_name, d.name AS doctor_name 
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    JOIN doctors d ON a.doctor_id = d.doctor_id
                """
                conditions = []
                params = []
                
                if doctor_id:
                    conditions.append("a.doctor_id = %s")
                    params.append(doctor_id)
                if patient_id:
                    conditions.append("a.patient_id = %s")
                    params.append(patient_id)
                    
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                    
                query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
                
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                # Return the detailed results containing names
                return rows
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch appointments: {e}")
        return results
