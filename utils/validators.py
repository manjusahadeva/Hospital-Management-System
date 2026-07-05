import re
from datetime import datetime
def validate_date(date_str):
    """Validates if date is in YYYY-MM-DD format and is a valid calendar date."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
def validate_time(time_str):
    """Validates if time is in HH:MM format."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False
def validate_phone(phone_str):
    """Validates if phone number is numeric and has length between 10 and 15 digits."""
    return phone_str.isdigit() and 10 <= len(phone_str) <= 15
def validate_email(email_str):
    """Validates simple email format using regular expressions."""
    if not email_str:
        return True  # Email is optional in schema
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email_str))
def validate_gender(gender_str):
    """Validates gender value against allowed database options."""
    return gender_str.title() in ["Male", "Female", "Other"]
def validate_positive_number(val_str):
    """Validates if a string is a valid positive float/integer."""
    try:
        val = float(val_str)
        return val >= 0
    except ValueError:
        return False
def validate_positive_int(val_str):
    """Validates if a string is a positive integer."""
    try:
        val = int(val_str)
        return val >= 0
    except ValueError:
        return False