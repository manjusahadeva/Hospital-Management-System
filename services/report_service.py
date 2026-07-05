from datetime import date
from database import DBConnection
from utils.validators import validate_date
class ReportService:
    """
    Business Logic Layer for Hospital Reports and Analytics.
    Provides query aggregations for patients, revenue, schedules, and pharmacy.
    """
    @staticmethod
    def get_daily_patients(report_date=None):
        """
        Retrieves patients who have appointments scheduled on a specific date.
        """
        if not report_date:
            report_date = str(date.today())
            
        if not validate_date(report_date):
            print("[Validation Error] Invalid date format. Use YYYY-MM-DD.")
            return []
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT a.appointment_id, a.appointment_time, p.patient_id, p.name AS patient_name, 
                           p.phone, d.name AS doctor_name, a.status
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    JOIN doctors d ON a.doctor_id = d.doctor_id
                    WHERE a.appointment_date = %s
                    ORDER BY a.appointment_time ASC
                """
                cursor.execute(query, (report_date,))
                return cursor.fetchall()
        except Exception as e:
            print(f"\n[Database Error] Failed to generate daily patients report: {e}")
        return []
    @staticmethod
    def get_daily_revenue(report_date=None):
        """
        Calculates total billed revenue and collected cash on a specific date.
        """
        if not report_date:
            report_date = str(date.today())
            
        if not validate_date(report_date):
            print("[Validation Error] Invalid date format. Use YYYY-MM-DD.")
            return None
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT COUNT(bill_id) AS total_bills,
                           COALESCE(SUM(total_amount), 0.00) AS total_billed,
                           COALESCE(SUM(paid_amount), 0.00) AS total_collected,
                           COALESCE(SUM(balance_amount), 0.00) AS total_outstanding
                    FROM bills
                    WHERE billing_date = %s
                """
                cursor.execute(query, (report_date,))
                return cursor.fetchone()
        except Exception as e:
            print(f"\n[Database Error] Failed to calculate daily revenue: {e}")
        return None
    @staticmethod
    def get_doctor_schedule(doctor_id, schedule_date=None):
        """
        Retrieves all appointments scheduled for a specific doctor on a specific date.
        """
        if not schedule_date:
            schedule_date = str(date.today())
            
        if not validate_date(schedule_date):
            print("[Validation Error] Invalid date format. Use YYYY-MM-DD.")
            return []
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT a.appointment_id, a.appointment_time, p.patient_id, p.name AS patient_name, 
                           a.status, a.reason
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    WHERE a.doctor_id = %s AND a.appointment_date = %s
                    ORDER BY a.appointment_time ASC
                """
                cursor.execute(query, (doctor_id, schedule_date))
                return cursor.fetchall()
        except Exception as e:
            print(f"\n[Database Error] Failed to get doctor schedule: {e}")
        return []
    @staticmethod
    def get_medicine_stock_report(low_stock_threshold=10):
        """
        Retrieves a report of all medicines in stock, highlighting ones that are
        expired or below the threshold.
        """
        try:
            with DBConnection() as (conn, cursor):
                query = """
                    SELECT medicine_id, name, manufacturer, price, stock_quantity, expiry_date,
                           (expiry_date <= CURRENT_DATE()) AS is_expired,
                           (stock_quantity <= %s) AS is_low_stock
                    FROM medicines
                    ORDER BY stock_quantity ASC, expiry_date ASC
                """
                cursor.execute(query, (low_stock_threshold,))
                return cursor.fetchall()
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch medicine stock report: {e}")
        return []
