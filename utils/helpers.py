import hashlib
import os
def hash_password(password):
    """Generates SHA-256 hash of a string to store passwords securely."""
    if not password:
        return ""
    return hashlib.sha256(password.encode()).hexdigest()
def generate_unique_id(prefix, table_name, col_name, cursor):
    """
    Generates a unique business ID for an entity by finding the maximum value
    in the database and incrementing the numeric suffix.
    E.g. PAT-10001 -> PAT-10002
    """
    query = f"SELECT {col_name} FROM {table_name} ORDER BY {col_name} DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    
    start_num = 10001
    
    if result and result[col_name]:
        last_id = result[col_name]
        try:
            # Assuming format: PREFIX-NUMBER (e.g., PAT-10001)
            parts = last_id.split('-')
            if len(parts) == 2 and parts[1].isdigit():
                next_num = int(parts[1]) + 1
                return f"{prefix}-{next_num}"
        except Exception:
            pass
            
    return f"{prefix}-{start_num}"
def clear_screen():
    """Clears the console screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')
def get_input(prompt, validator_func=None, error_msg="Invalid input. Please try again.", optional=False):
    """
    Helper function to get validated input from the console.
    Keeps prompting the user until the input is valid.
    """
    while True:
        value = input(prompt).strip()
        if not value:
            if optional:
                return None
            print("[Error] This field cannot be empty.")
            continue
            
        if validator_func:
            if validator_func(value):
                return value
            else:
                print(f"[Error] {error_msg}")
        else:
            return value