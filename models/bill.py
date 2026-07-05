class Bill:
    def __init__(self, patient_id, total_amount, billing_date, appointment_id=None, paid_amount=0.00, payment_status="Unpaid", bill_id=None, created_at=None):
        self.bill_id = bill_id  # Unique string identifier, e.g., BIL-10001
        self.patient_id = patient_id
        self.appointment_id = appointment_id
        self.total_amount = float(total_amount)
        self.paid_amount = float(paid_amount)
        self.balance_amount = self.total_amount - self.paid_amount
        self.payment_status = payment_status  # Unpaid, Partially Paid, Paid
        self.billing_date = billing_date  # YYYY-MM-DD
        self.created_at = created_at
    def __repr__(self):
        return f"Bill(id='{self.bill_id}', total={self.total_amount}, paid={self.paid_amount}, status='{self.payment_status}')"
