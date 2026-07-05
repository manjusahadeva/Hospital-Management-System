import sys
from database import initialize_database
from services.auth_service import AuthService
from services.patient_service import PatientService
from services.doctor_service import DoctorService
from services.appt_service import AppointmentService
from services.bill_service import BillService
from services.pharmacy_service import PharmacyService
from services.report_service import ReportService
from utils.helpers import get_input, clear_screen
from utils.validators import (
    validate_date, validate_time, validate_phone, 
    validate_email, validate_gender, validate_positive_number, 
    validate_positive_int
)
# Current Logged-in User Context
current_user = None
def print_header(title):
    """Prints a standard stylized header for CLI screens."""
    print("=" * 60)
    print(f"{title.center(60)}")
    print("=" * 60)
def main_menu():
    """Main CLI program loop. Performs initialization and handles Login/Exit."""
    global current_user
    
    print("\nInitializing database connection...")
    if not initialize_database():
        print("[Fatal Error] Could not initialize database. Exiting application.")
        sys.exit(1)
        
    while True:
        clear_screen()
        print_header("HOSPITAL MANAGEMENT SYSTEM")
        print("1. Login")
        print("2. Exit")
        print("-" * 60)
        
        choice = get_input("Select an option (1-2): ", lambda x: x in ['1', '2'], "Invalid choice. Select 1 or 2.")
        
        if choice == '1':
            login_flow()
        elif choice == '2':
            print("\nThank you for using the Hospital Management System. Goodbye!")
            sys.exit(0)
def login_flow():
    """Handles the user authentication prompt and redirects to role menus."""
    global current_user
    clear_screen()
    print_header("USER LOGIN")
    
    username = get_input("Username: ")
    password = get_input("Password: ")  # Raw password input, will be hashed in AuthService
    
    print("\nAuthenticating...")
    user = AuthService.login(username, password)
    
    if user:
        current_user = user
        print(f"\n[Success] Welcome back, {user.username}! Role: {user.role}")
        input("Press Enter to continue...")
        
        if user.role == 'Admin':
            admin_dashboard()
        elif user.role == 'Doctor':
            doctor_dashboard()
        elif user.role == 'Receptionist':
            receptionist_dashboard()
    else:
        print("\n[Error] Invalid username or password.")
        input("Press Enter to try again...")
# =========================================================================
# DASHBOARDS
# =========================================================================
def admin_dashboard():
    """Displays dashboard for Administrators."""
    while True:
        clear_screen()
        print_header(f"ADMIN DASHBOARD | User: {current_user.username}")
        print("1. Patient Management")
        print("2. Doctor Management")
        print("3. Appointment Management")
        print("4. Billing Management")
        print("5. Pharmacy Management")
        print("6. Hospital Reports")
        print("7. Logout")
        print("-" * 60)
        
        choice = get_input("Select an option (1-7): ", lambda x: x in [str(i) for i in range(1, 8)], "Invalid option.")
        
        if choice == '1':
            patient_menu()
        elif choice == '2':
            doctor_menu()
        elif choice == '3':
            appointment_menu()
        elif choice == '4':
            billing_menu()
        elif choice == '5':
            pharmacy_menu()
        elif choice == '6':
            reports_menu()
        elif choice == '7':
            print("\nLogging out...")
            break
def receptionist_dashboard():
    """Displays dashboard for Receptionists."""
    while True:
        clear_screen()
        print_header(f"RECEPTIONIST DASHBOARD | User: {current_user.username}")
        print("1. Patient Management")
        print("2. Appointment Booking")
        print("3. Billing Management")
        print("4. Logout")
        print("-" * 60)
        
        choice = get_input("Select an option (1-4): ", lambda x: x in ['1', '2', '3', '4'], "Invalid option.")
        
        if choice == '1':
            patient_menu()
        elif choice == '2':
            appointment_menu()
        elif choice == '3':
            billing_menu()
        elif choice == '4':
            print("\nLogging out...")
            break
def doctor_dashboard():
    """Displays dashboard for Doctors."""
    # Find matching doctor_id from database
    doctor_profile = DoctorService.get_doctor_by_user_id(current_user.user_id)
    if not doctor_profile:
        print("\n[Error] No doctor profile associated with this account.")
        input("Press Enter to log out...")
        return
    while True:
        clear_screen()
        print_header(f"DOCTOR DASHBOARD | Dr. {doctor_profile.name} ({doctor_profile.specialization})")
        print("1. View My Appointments (Today)")
        print("2. Search Patients")
        print("3. View Medicine Inventory")
        print("4. Logout")
        print("-" * 60)
        
        choice = get_input("Select an option (1-4): ", lambda x: x in ['1', '2', '3', '4'], "Invalid option.")
        
        if choice == '1':
            view_doctor_appointments(doctor_profile.doctor_id)
        elif choice == '2':
            search_patients_flow()
        elif choice == '3':
            view_all_medicines_flow()
        elif choice == '4':
            print("\nLogging out...")
            break
# =========================================================================
# SUBMENUS & FLOWS
# =========================================================================
# --- 1. PATIENT MANAGEMENT ---
def patient_menu():
    while True:
        clear_screen()
        print_header("PATIENT MANAGEMENT")
        print("1. Add Patient")
        print("2. Update Patient")
        print("3. Delete Patient")
        print("4. Search Patient")
        print("5. View All Patients")
        print("6. Back to Dashboard")
        print("-" * 60)
        
        choice = get_input("Select an option (1-6): ", lambda x: x in ['1', '2', '3', '4', '5', '6'], "Invalid option.")
        
        if choice == '1':
            add_patient_flow()
        elif choice == '2':
            update_patient_flow()
        elif choice == '3':
            delete_patient_flow()
        elif choice == '4':
            search_patients_flow()
        elif choice == '5':
            view_all_patients_flow()
        elif choice == '6':
            break
def add_patient_flow():
    clear_screen()
    print_header("ADD PATIENT")
    name = get_input("Enter Patient Name: ")
    dob = get_input("Enter Date of Birth (YYYY-MM-DD): ", validate_date, "Must be YYYY-MM-DD")
    gender = get_input("Enter Gender (Male/Female/Other): ", validate_gender, "Must be Male, Female, or Other")
    phone = get_input("Enter Phone Number: ", validate_phone, "Must be 10-15 digits")
    email = get_input("Enter Email (Optional, press enter to skip): ", validate_email, "Invalid email format", optional=True)
    address = get_input("Enter Address (Optional, press enter to skip): ", optional=True)
    
    PatientService.add_patient(name, dob, gender, phone, email, address)
    input("\nPress Enter to return...")
def update_patient_flow():
    clear_screen()
    print_header("UPDATE PATIENT")
    patient_id = get_input("Enter Patient ID (e.g. PAT-10001): ")
    
    # Verify patient exists first
    patient = PatientService.get_patient_by_id(patient_id)
    if not patient:
        print(f"\n[Error] Patient with ID '{patient_id}' not found.")
        input("Press Enter to return...")
        return
        
    print(f"\nEditing Patient details for {patient.name}. Enter new details or press Enter to keep current values.")
    name = get_input(f"Name [{patient.name}]: ", optional=True)
    dob = get_input(f"DOB [{patient.dob}]: ", validate_date, "Must be YYYY-MM-DD", optional=True)
    gender = get_input(f"Gender [{patient.gender}]: ", validate_gender, "Must be Male, Female, or Other", optional=True)
    phone = get_input(f"Phone [{patient.phone}]: ", validate_phone, "Must be 10-15 digits", optional=True)
    email = get_input(f"Email [{patient.email or 'N/A'}]: ", validate_email, "Invalid email", optional=True)
    address = get_input(f"Address [{patient.address or 'N/A'}]: ", optional=True)
    
    PatientService.update_patient(patient_id, name, dob, gender, phone, email, address)
    input("\nPress Enter to return...")
def delete_patient_flow():
    clear_screen()
    print_header("DELETE PATIENT")
    patient_id = get_input("Enter Patient ID to delete: ")
    
    confirm = get_input(f"Are you sure you want to delete Patient '{patient_id}'? (yes/no): ").lower()
    if confirm == 'yes':
        PatientService.delete_patient(patient_id)
    else:
        print("[Cancelled] Deletion cancelled.")
    input("\nPress Enter to return...")
def search_patients_flow():
    clear_screen()
    print_header("SEARCH PATIENT")
    term = get_input("Enter search query (ID, Name, or Phone): ")
    
    results = PatientService.search_patients(term)
    if results:
        print(f"\nFound {len(results)} patient(s):")
        print(f"{'Patient ID':<12} | {'Name':<20} | {'DOB':<12} | {'Gender':<8} | {'Phone':<12}")
        print("-" * 70)
        for p in results:
            print(f"{p.patient_id:<12} | {p.name:<20} | {p.dob:<12} | {p.gender:<8} | {p.phone:<12}")
    else:
        print("\nNo patients match the search term.")
    input("\nPress Enter to continue...")
def view_all_patients_flow():
    clear_screen()
    print_header("VIEW ALL PATIENTS")
    patients = PatientService.get_all_patients()
    if patients:
        print(f"{'Patient ID':<12} | {'Name':<20} | {'DOB':<12} | {'Gender':<8} | {'Phone':<12}")
        print("-" * 75)
        for p in patients:
            print(f"{p.patient_id:<12} | {p.name:<20} | {p.dob:<12} | {p.gender:<8} | {p.phone:<12}")
    else:
        print("No patients registered in the database.")
    input("\nPress Enter to return...")
# --- 2. DOCTOR MANAGEMENT (Admin only) ---
def doctor_menu():
    if current_user.role != 'Admin':
        print("\n[Access Denied] Only Administrators can access Doctor Management.")
        input("Press Enter to return...")
        return
        
    while True:
        clear_screen()
        print_header("DOCTOR MANAGEMENT")
        print("1. Add Doctor")
        print("2. Update Doctor")
        print("3. Delete Doctor")
        print("4. Search Doctor")
        print("5. View All Doctors")
        print("6. Back to Dashboard")
        print("-" * 60)
        
        choice = get_input("Select an option (1-6): ", lambda x: x in ['1', '2', '3', '4', '5', '6'], "Invalid option.")
        
        if choice == '1':
            add_doctor_flow()
        elif choice == '2':
            update_doctor_flow()
        elif choice == '3':
            delete_doctor_flow()
        elif choice == '4':
            search_doctors_flow()
        elif choice == '5':
            view_all_doctors_flow()
        elif choice == '6':
            break
def add_doctor_flow():
    clear_screen()
    print_header("ADD DOCTOR")
    name = get_input("Enter Doctor Name (e.g. Dr. John): ")
    specialization = get_input("Enter Specialization (e.g. Cardiology): ")
    phone = get_input("Enter Phone Number: ", validate_phone, "Must be 10-15 digits")
    email = get_input("Enter Email (Optional): ", validate_email, "Invalid email format", optional=True)
    qualification = get_input("Enter Qualifications (e.g. MD, DM, MBBS): ", optional=True)
    
    print("\n--- Setup Login Account for Doctor ---")
    username = get_input("Choose Username: ")
    password = get_input("Choose Password: ")
    
    DoctorService.add_doctor(name, specialization, phone, email, qualification, username, password)
    input("\nPress Enter to return...")
def update_doctor_flow():
    clear_screen()
    print_header("UPDATE DOCTOR")
    doctor_id = get_input("Enter Doctor ID (e.g. DOC-10001): ")
    
    doctor = DoctorService.get_doctor_by_id(doctor_id)
    if not doctor:
        print(f"\n[Error] Doctor with ID '{doctor_id}' not found.")
        input("Press Enter to return...")
        return
        
    print(f"\nEditing Doctor profile for {doctor.name}. Enter new details or press Enter to keep current values.")
    name = get_input(f"Name [{doctor.name}]: ", optional=True)
    specialization = get_input(f"Specialization [{doctor.specialization}]: ", optional=True)
    phone = get_input(f"Phone [{doctor.phone}]: ", validate_phone, "Must be 10-15 digits", optional=True)
    email = get_input(f"Email [{doctor.email or 'N/A'}]: ", validate_email, "Invalid email", optional=True)
    qualification = get_input(f"Qualifications [{doctor.qualification or 'N/A'}]: ", optional=True)
    
    DoctorService.update_doctor(doctor_id, name, specialization, phone, email, qualification)
    input("\nPress Enter to return...")
def delete_doctor_flow():
    clear_screen()
    print_header("DELETE DOCTOR")
    doctor_id = get_input("Enter Doctor ID to delete: ")
    
    confirm = get_input(f"Are you sure you want to delete Doctor '{doctor_id}' and their linked login account? (yes/no): ").lower()
    if confirm == 'yes':
        DoctorService.delete_doctor(doctor_id)
    else:
        print("[Cancelled] Deletion cancelled.")
    input("\nPress Enter to return...")
def search_doctors_flow():
    clear_screen()
    print_header("SEARCH DOCTOR")
    term = get_input("Enter search query (ID, Name, Specialization, or Phone): ")
    
    results = DoctorService.search_doctors(term)
    if results:
        print(f"\nFound {len(results)} doctor(s):")
        print(f"{'Doctor ID':<12} | {'Name':<20} | {'Specialization':<18} | {'Phone':<12}")
        print("-" * 70)
        for d in results:
            print(f"{d.doctor_id:<12} | {d.name:<20} | {d.specialization:<18} | {d.phone:<12}")
    else:
        print("\nNo doctors match the search term.")
    input("\nPress Enter to continue...")
def view_all_doctors_flow():
    clear_screen()
    print_header("VIEW ALL DOCTORS")
    doctors = DoctorService.get_all_doctors()
    if doctors:
        print(f"{'Doctor ID':<12} | {'Name':<20} | {'Specialization':<18} | {'Phone':<12}")
        print("-" * 70)
        for d in doctors:
            print(f"{d.doctor_id:<12} | {d.name:<20} | {d.specialization:<18} | {d.phone:<12}")
    else:
        print("No doctors registered in the database.")
    input("\nPress Enter to return...")
# --- 3. APPOINTMENT MANAGEMENT ---
def appointment_menu():
    while True:
        clear_screen()
        print_header("APPOINTMENT MANAGEMENT")
        print("1. Book Appointment")
        print("2. Cancel Appointment")
        print("3. Mark Appointment Completed")
        print("4. View All Appointments")
        print("5. Back to Dashboard")
        print("-" * 60)
        
        choice = get_input("Select an option (1-5): ", lambda x: x in ['1', '2', '3', '4', '5'], "Invalid option.")
        
        if choice == '1':
            book_appointment_flow()
        elif choice == '2':
            cancel_appointment_flow()
        elif choice == '3':
            complete_appointment_flow()
        elif choice == '4':
            view_appointments_flow()
        elif choice == '5':
            break
def book_appointment_flow():
    clear_screen()
    print_header("BOOK APPOINTMENT")
    patient_id = get_input("Enter Patient ID (e.g. PAT-10001): ")
    doctor_id = get_input("Enter Doctor ID (e.g. DOC-10001): ")
    appointment_date = get_input("Enter Appointment Date (YYYY-MM-DD): ", validate_date, "Must be YYYY-MM-DD")
    appointment_time = get_input("Enter Appointment Time (HH:MM): ", validate_time, "Must be HH:MM")
    reason = get_input("Enter Reason for Appointment (Optional): ", optional=True)
    
    AppointmentService.book_appointment(patient_id, doctor_id, appointment_date, appointment_time, reason)
    input("\nPress Enter to return...")
def cancel_appointment_flow():
    clear_screen()
    print_header("CANCEL APPOINTMENT")
    appointment_id = get_input("Enter Appointment ID (e.g. APT-10001): ")
    
    confirm = get_input(f"Cancel Appointment '{appointment_id}'? (yes/no): ").lower()
    if confirm == 'yes':
        AppointmentService.cancel_appointment(appointment_id)
    else:
        print("[Cancelled] Operation aborted.")
    input("\nPress Enter to return...")
def complete_appointment_flow():
    clear_screen()
    print_header("COMPLETE APPOINTMENT")
    appointment_id = get_input("Enter Appointment ID (e.g. APT-10001): ")
    AppointmentService.complete_appointment(appointment_id)
    input("\nPress Enter to return...")
def view_appointments_flow():
    clear_screen()
    print_header("VIEW ALL APPOINTMENTS")
    appts = AppointmentService.get_appointments()
    if appts:
        print(f"{'Appt ID':<10} | {'Patient Name':<18} | {'Doctor Name':<18} | {'Date':<11} | {'Time':<7} | {'Status':<10}")
        print("-" * 85)
        for a in appts:
            print(f"{a['appointment_id']:<10} | {a['patient_name']:<18} | {a['doctor_name']:<18} | {str(a['appointment_date']):<11} | {str(a['appointment_time'])[:5]:<7} | {a['status']:<10}")
    else:
        print("No appointments found.")
    input("\nPress Enter to return...")
def view_doctor_appointments(doctor_id):
    """Doctor dashboard flow to see their appointments."""
    clear_screen()
    print_header("MY APPOINTMENTS")
    appts = AppointmentService.get_appointments(doctor_id=doctor_id)
    if appts:
        print(f"{'Appt ID':<10} | {'Patient Name':<18} | {'Date':<11} | {'Time':<7} | {'Status':<10} | {'Reason':<15}")
        print("-" * 80)
        for a in appts:
            print(f"{a['appointment_id']:<10} | {a['patient_name']:<18} | {str(a['appointment_date']):<11} | {str(a['appointment_time'])[:5]:<7} | {a['status']:<10} | {a['reason'] or 'N/A':<15}")
    else:
        print("No appointments scheduled for you.")
    input("\nPress Enter to return...")
# --- 4. BILLING MANAGEMENT ---
def billing_menu():
    while True:
        clear_screen()
        print_header("BILLING MANAGEMENT")
        print("1. Generate Bill")
        print("2. Record Payment")
        print("3. View All Bills")
        print("4. View Bills by Patient")
        print("5. Back to Dashboard")
        print("-" * 60)
        
        choice = get_input("Select an option (1-5): ", lambda x: x in ['1', '2', '3', '4', '5'], "Invalid option.")
        
        if choice == '1':
            generate_bill_flow()
        elif choice == '2':
            record_payment_flow()
        elif choice == '3':
            view_all_bills_flow()
        elif choice == '4':
            view_patient_bills_flow()
        elif choice == '5':
            break
def generate_bill_flow():
    clear_screen()
    print_header("GENERATE BILL")
    patient_id = get_input("Enter Patient ID: ")
    total_amount = get_input("Enter Total Amount ($): ", validate_positive_number, "Must be a positive float number")
    paid_amount = get_input("Enter Paid Amount ($) (default 0.00): ", validate_positive_number, "Must be positive", optional=True) or 0.00
    appointment_id = get_input("Enter Appointment ID (Optional, press Enter to skip): ", optional=True)
    billing_date = get_input("Enter Billing Date (YYYY-MM-DD, press Enter for Today): ", validate_date, "Must be YYYY-MM-DD", optional=True)
    
    BillService.generate_bill(patient_id, total_amount, paid_amount, billing_date, appointment_id)
    input("\nPress Enter to return...")
def record_payment_flow():
    clear_screen()
    print_header("RECORD PAYMENT")
    bill_id = get_input("Enter Bill ID (e.g. BIL-10001): ")
    amount = get_input("Enter Payment Amount ($): ", validate_positive_number, "Must be a positive float number")
    
    BillService.record_payment(bill_id, amount)
    input("\nPress Enter to return...")
def view_all_bills_flow():
    clear_screen()
    print_header("VIEW ALL BILLS")
    bills = BillService.get_all_bills()
    if bills:
        print(f"{'Bill ID':<10} | {'Patient Name':<18} | {'Total ($)':<10} | {'Paid ($)':<10} | {'Balance ($)':<11} | {'Status':<10}")
        print("-" * 80)
        for b in bills:
            print(f"{b['bill_id']:<10} | {b['patient_name']:<18} | {b['total_amount']:<10.2f} | {b['paid_amount']:<10.2f} | {b['balance_amount']:<11.2f} | {b['payment_status']:<10}")
    else:
        print("No invoices generated yet.")
    input("\nPress Enter to return...")
def view_patient_bills_flow():
    clear_screen()
    print_header("VIEW PATIENT BILLS")
    patient_id = get_input("Enter Patient ID: ")
    bills = BillService.get_bills_by_patient(patient_id)
    if bills:
        print(f"\nBills for Patient {patient_id}:")
        print(f"{'Bill ID':<10} | {'Total ($)':<10} | {'Paid ($)':<10} | {'Balance ($)':<11} | {'Status':<10}")
        print("-" * 60)
        for b in bills:
            print(f"{b['bill_id']:<10} | {b['total_amount']:<10.2f} | {b['paid_amount']:<10.2f} | {b['balance_amount']:<11.2f} | {b['payment_status']:<10}")
    else:
        print("\nNo bills found for this patient.")
    input("\nPress Enter to continue...")
# --- 5. PHARMACY MANAGEMENT ---
def pharmacy_menu():
    while True:
        clear_screen()
        print_header("PHARMACY MANAGEMENT")
        print("1. Add Medicine to Stock")
        print("2. Update Stock Levels")
        print("3. View Medicine Inventory")
        print("4. Back to Dashboard")
        print("-" * 60)
        
        choice = get_input("Select an option (1-4): ", lambda x: x in ['1', '2', '3', '4'], "Invalid option.")
        
        if choice == '1':
            add_medicine_flow()
        elif choice == '2':
            update_medicine_stock_flow()
        elif choice == '3':
            view_all_medicines_flow()
        elif choice == '4':
            break
def add_medicine_flow():
    clear_screen()
    print_header("ADD MEDICINE TO STOCK")
    name = get_input("Enter Medicine Name: ")
    manufacturer = get_input("Enter Manufacturer (Optional): ", optional=True)
    description = get_input("Enter Description (Optional): ", optional=True)
    price = get_input("Enter Unit Price ($): ", validate_positive_number, "Must be a positive float number")
    quantity = get_input("Enter Initial Stock Quantity: ", validate_positive_int, "Must be positive integer")
    expiry = get_input("Enter Expiry Date (YYYY-MM-DD): ", validate_date, "Must be YYYY-MM-DD")
    
    PharmacyService.add_medicine(name, price, quantity, expiry, manufacturer, description)
    input("\nPress Enter to return...")
def update_medicine_stock_flow():
    clear_screen()
    print_header("UPDATE MEDICINE STOCK")
    medicine_id = get_input("Enter Medicine ID (from list): ", validate_positive_int, "Must be numeric ID")
    quantity = get_input("Enter New Stock Quantity: ", validate_positive_int, "Must be positive integer")
    
    PharmacyService.update_stock(int(medicine_id), int(quantity))
    input("\nPress Enter to return...")
def view_all_medicines_flow():
    clear_screen()
    print_header("MEDICINE INVENTORY")
    medicines = PharmacyService.get_all_medicines()
    if medicines:
        print(f"{'ID':<4} | {'Name':<22} | {'Manufacturer':<15} | {'Price ($)':<9} | {'Stock':<6} | {'Expiry':<10}")
        print("-" * 75)
        for m in medicines:
            print(f"{m.medicine_id:<4} | {m.name:<22} | {(m.manufacturer or 'N/A'):<15} | {m.price:<9.2f} | {m.stock_quantity:<6} | {m.expiry_date:<10}")
    else:
        print("Pharmacy inventory is empty.")
    input("\nPress Enter to continue...")
# --- 6. HOSPITAL REPORTS (Admin only) ---
def reports_menu():
    if current_user.role != 'Admin':
        print("\n[Access Denied] Only Administrators can view analytics reports.")
        input("Press Enter to return...")
        return
        
    while True:
        clear_screen()
        print_header("HOSPITAL REPORTS & ANALYTICS")
        print("1. Daily Patients Report")
        print("2. Daily Revenue Report")
        print("3. Doctor Schedule Report")
        print("4. Medicine Stock and Expiry Report")
        print("5. Back to Dashboard")
        print("-" * 60)
        
        choice = get_input("Select an option (1-5): ", lambda x: x in ['1', '2', '3', '4', '5'], "Invalid option.")
        
        if choice == '1':
            daily_patients_report_flow()
        elif choice == '2':
            daily_revenue_report_flow()
        elif choice == '3':
            doctor_schedule_report_flow()
        elif choice == '4':
            medicine_stock_report_flow()
        elif choice == '5':
            break
def daily_patients_report_flow():
    clear_screen()
    print_header("DAILY PATIENTS REPORT")
    rep_date = get_input("Enter Date (YYYY-MM-DD, press Enter for Today): ", validate_date, "Must be YYYY-MM-DD", optional=True)
    
    rows = ReportService.get_daily_patients(rep_date)
    date_label = rep_date if rep_date else str(date.today())
    print(f"\nScheduled Patients for: {date_label}")
    if rows:
        print(f"{'Appt ID':<10} | {'Time':<6} | {'Patient ID':<10} | {'Patient Name':<15} | {'Doctor Name':<15} | {'Status':<10}")
        print("-" * 80)
        for r in rows:
            print(f"{r['appointment_id']:<10} | {str(r['appointment_time'])[:5]:<6} | {r['patient_id']:<10} | {r['patient_name']:<15} | {r['doctor_name']:<15} | {r['status']:<10}")
    else:
        print("No patients scheduled on this date.")
    input("\nPress Enter to continue...")
def daily_revenue_report_flow():
    clear_screen()
    print_header("DAILY REVENUE REPORT")
    rep_date = get_input("Enter Date (YYYY-MM-DD, press Enter for Today): ", validate_date, "Must be YYYY-MM-DD", optional=True)
    
    rev = ReportService.get_daily_revenue(rep_date)
    date_label = rep_date if rep_date else str(date.today())
    print(f"\nRevenue details for: {date_label}")
    if rev and rev['total_bills'] > 0:
        print(f"Total Bills Raised  : {rev['total_bills']}")
        print(f"Total Amount Billed  : ${rev['total_billed']:.2f}")
        print(f"Total Cash Collected : ${rev['total_collected']:.2f}")
        print(f"Outstanding Balance  : ${rev['total_outstanding']:.2f}")
    else:
        print("No revenue activity recorded on this date.")
    input("\nPress Enter to continue...")
def doctor_schedule_report_flow():
    clear_screen()
    print_header("DOCTOR SCHEDULE REPORT")
    doctor_id = get_input("Enter Doctor ID (e.g. DOC-10001): ")
    rep_date = get_input("Enter Date (YYYY-MM-DD, press Enter for Today): ", validate_date, "Must be YYYY-MM-DD", optional=True)
    
    doctor = DoctorService.get_doctor_by_id(doctor_id)
    if not doctor:
        print(f"[Error] Doctor '{doctor_id}' not found.")
        input("\nPress Enter to return...")
        return
        
    rows = ReportService.get_doctor_schedule(doctor_id, rep_date)
    date_label = rep_date if rep_date else str(date.today())
    print(f"\nSchedule for Dr. {doctor.name} on {date_label}:")
    if rows:
        print(f"{'Appt ID':<10} | {'Time':<6} | {'Patient ID':<10} | {'Patient Name':<18} | {'Status':<10}")
        print("-" * 65)
        for r in rows:
            print(f"{r['appointment_id']:<10} | {str(r['appointment_time'])[:5]:<6} | {r['patient_id']:<10} | {r['patient_name']:<18} | {r['status']:<10}")
    else:
        print("No schedule/appointments found for this date.")
    input("\nPress Enter to continue...")
def medicine_stock_report_flow():
    clear_screen()
    print_header("PHARMACY STOCK AND EXPIRY REPORT")
    rows = ReportService.get_medicine_stock_report()
    if rows:
        print(f"{'ID':<4} | {'Name':<22} | {'Stock':<6} | {'Expiry':<10} | {'Status Alerts'}")
        print("-" * 75)
        for r in rows:
            alerts = []
            if r['is_expired']:
                alerts.append("EXPIRED")
            elif r['is_low_stock']:
                alerts.append("LOW STOCK")
            
            alert_str = ", ".join(alerts) if alerts else "Healthy"
            print(f"{r['medicine_id']:<4} | {r['name']:<22} | {r['stock_quantity']:<6} | {str(r['expiry_date']):<10} | {alert_str}")
    else:
        print("No inventory available.")
    input("\nPress Enter to continue...")
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Exiting safely.")
        sys.exit(0)

