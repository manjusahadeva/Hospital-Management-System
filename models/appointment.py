class Appointment:
    def __init__(self, patient_id, doctor_id, appointment_date, appointment_time, reason=None, status="Scheduled", appointment_id=None, created_at=None):
        self.appointment_id = appointment_id  # Unique string identifier, e.g., APT-10001
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date  # YYYY-MM-DD
        self.appointment_time = appointment_time  # HH:MM
        self.reason = reason
        self.status = status  # Scheduled, Completed, Cancelled
        self.created_at = created_at
    def __repr__(self):
        return f"Appointment(id='{self.appointment_id}', patient='{self.patient_id}', doctor='{self.doctor_id}', date='{self.appointment_date}', status='{self.status}')"
