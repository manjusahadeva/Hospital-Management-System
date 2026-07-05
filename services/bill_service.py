from datetime import date
from database import DBConnection
from models.bill import Bill
from utils.helpers import generate_unique_id
from utils.validators import validate_date, validate_positive_number
from services.patient_service import PatientService
class BillService:
    """
    Business Logic Layer for Billing and Financial transactions.
    Calculates balance amounts, payment status, and handles payments.
    """
    @staticmethod
    def generate_bill(patient_id, total_amount, paid_amount=0.00, billing_date=None, appointment_id=None):
        """
        Generates a new invoice for a patient.
        Automatically calculates balance and sets status.
        """
        # Set default date if none provided
        if not billing_date:
            billing_date = str(date.today())
        # Validations
        if not validate_date(billing_date):
            print("[Validation Error] Invalid Billing Date. Use YYYY-MM-DD.")
            return None
        if not validate_positive_number(str(total_amount)) or float(total_amount) <= 0:
            print("[Validation Error] Total amount must be a positive number.")
            return None
        if not validate_positive_number(str(paid_amount)) or float(paid_amount) < 0:
            print("[Validation Error] Paid amount cannot be negative.")
            return None
        total_amount = float(total_amount)
        paid_amount = float(paid_amount)
        if paid_amount > total_amount:
            print("[Validation Error] Paid amount cannot exceed total amount.")
            return None
        # Verify patient exists
        patient = PatientService.get_patient_by_id(patient_id)
        if not patient:
            print(f"[Error] Patient with ID '{patient_id}' does not exist.")
            return None
        # Calculate balance and status
        balance_amount = total_amount - paid_amount
        if paid_amount == 0:
            payment_status = "Unpaid"
        elif balance_amount == 0:
            payment_status = "Paid"
        else:
            payment_status = "Partially Paid"
        try:
            with DBConnection() as (conn, cursor):
                # Check if appointment_id already has a bill (if provided)
                if appointment_id:
                    cursor.execute("SELECT bill_id FROM bills WHERE appointment_id = %s", (appointment_id,))
                    if cursor.fetchone():
                        print(f"[Billing Error] A bill has already been generated for Appointment '{appointment_id}'.")
                        return None
                
                # Generate Bill ID
                bill_id = generate_unique_id("BIL", "bills", "bill_id", cursor)
                
                query = """
                    INSERT INTO bills (bill_id, patient_id, appointment_id, total_amount, paid_amount, balance_amount, payment_status, billing_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    bill_id, 
                    patient_id, 
                    appointment_id, 
                    total_amount, 
                    paid_amount, 
                    balance_amount, 
                    payment_status, 
                    billing_date
                ))
                
                print(f"\n[Success] Bill generated successfully! ID: {bill_id} | Status: {payment_status}")
                return bill_id
        except Exception as e:
            print(f"\n[Database Error] Failed to generate bill: {e}")
            return None
    @staticmethod
    def record_payment(bill_id, amount_paid):
        """
        Records a new payment towards an existing invoice, recalculating the status.
        """
        if not validate_positive_number(str(amount_paid)) or float(amount_paid) <= 0:
            print("[Validation Error] Payment amount must be a positive number.")
            return False
        amount_paid = float(amount_paid)
        try:
            with DBConnection() as (conn, cursor):
                # Retrieve current bill state
                cursor.execute("SELECT total_amount, paid_amount, balance_amount FROM bills WHERE bill_id = %s", (bill_id,))
                bill = cursor.fetchone()
                if not bill:
                    print(f"[Error] Bill with ID '{bill_id}' not found.")
                    return False
                total = float(bill['total_amount'])
                current_paid = float(bill['paid_amount'])
                current_balance = float(bill['balance_amount'])
                if current_balance == 0:
                    print("[Warning] This bill is already fully Paid.")
                    return True
                if amount_paid > current_balance:
                    print(f"[Validation Error] Payment of {amount_paid} exceeds the outstanding balance of {current_balance}.")
                    return False
                # Calculate new states
                new_paid = current_paid + amount_paid
                new_balance = total - new_paid
                
                if new_balance == 0:
                    new_status = "Paid"
                else:
                    new_status = "Partially Paid"
                # Update DB
                update_query = """
                    UPDATE bills 
                    SET paid_amount = %s, balance_amount = %s, payment_status = %s 
                    WHERE bill_id = %s
                """
                cursor.execute(update_query, (new_paid, new_balance, new_status, bill_id))
                print(f"\n[Success] Payment of ${amount_paid:.2f} recorded for Bill '{bill_id}'.")
                print(f"New Balance: ${new_balance:.2f} | Status: {new_status}")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to record payment: {e}")
            return False
    @staticmethod
    def get_all_bills():
        """
        Retrieves all bills joined with patient information.
        """
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT b.*, p.name AS patient_name 
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    ORDER BY b.billing_date DESC, b.created_at DESC
                """
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch bills: {e}")
        return []
    @staticmethod
    def get_bills_by_patient(patient_id):
        """
        Retrieves all bills for a specific patient.
        """
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT b.*, p.name AS patient_name 
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    WHERE b.patient_id = %s
                    ORDER BY b.billing_date DESC
                """
                cursor.execute(query, (patient_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch bills for patient: {e}")
        return []
