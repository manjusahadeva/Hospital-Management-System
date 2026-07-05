from database import DBConnection
from models.medicine import Medicine
from utils.validators import validate_date, validate_positive_number, validate_positive_int
class PharmacyService:
    """
    Business Logic Layer for Pharmacy Stock Management.
    """
    @staticmethod
    def add_medicine(name, price, stock_quantity, expiry_date, manufacturer=None, description=None):
        """
        Adds a new medicine to the inventory.
        """
        # Validations
        if not name.strip():
            print("[Validation Error] Medicine name cannot be empty.")
            return None
        if not validate_positive_number(str(price)) or float(price) <= 0:
            print("[Validation Error] Price must be a positive number.")
            return None
        if not validate_positive_int(str(stock_quantity)):
            print("[Validation Error] Stock quantity must be a positive integer.")
            return None
        if not validate_date(expiry_date):
            print("[Validation Error] Invalid Expiry Date. Use YYYY-MM-DD.")
            return None
        price = float(price)
        stock_quantity = int(stock_quantity)
        try:
            with DBConnection() as (conn, cursor):
                # Check duplicate name
                cursor.execute("SELECT medicine_id FROM medicines WHERE name = %s", (name.strip(),))
                if cursor.fetchone():
                    print(f"[Error] Medicine with name '{name}' already exists in inventory. Update stock instead.")
                    return None
                query = """
                    INSERT INTO medicines (name, manufacturer, description, price, stock_quantity, expiry_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    name.strip(), 
                    manufacturer, 
                    description, 
                    price, 
                    stock_quantity, 
                    expiry_date
                ))
                med_id = cursor.lastrowid
                print(f"\n[Success] Medicine '{name}' added successfully! ID: {med_id}")
                return med_id
        except Exception as e:
            print(f"\n[Database Error] Failed to add medicine: {e}")
            return None
    @staticmethod
    def update_stock(medicine_id, new_quantity):
        """
        Sets a new stock level for an existing medicine in inventory.
        """
        if not validate_positive_int(str(new_quantity)):
            print("[Validation Error] Stock quantity must be a positive integer.")
            return False
        new_quantity = int(new_quantity)
        try:
            with DBConnection() as (conn, cursor):
                # Verify existence
                cursor.execute("SELECT name FROM medicines WHERE medicine_id = %s", (medicine_id,))
                if not cursor.fetchone():
                    print(f"[Error] Medicine with ID {medicine_id} not found.")
                    return False
                query = "UPDATE medicines SET stock_quantity = %s WHERE medicine_id = %s"
                cursor.execute(query, (new_quantity, medicine_id))
                print(f"\n[Success] Stock updated successfully to {new_quantity} units.")
                return True
        except Exception as e:
            print(f"\n[Database Error] Failed to update stock: {e}")
            return False
    @staticmethod
    def get_all_medicines():
        """
        Retrieves all medicines from the pharmacy inventory.
        """
        medicines = []
        try:
            with DBConnection() as (conn, cursor):
                cursor.execute("SELECT * FROM medicines ORDER BY name ASC")
                rows = cursor.fetchall()
                for row in rows:
                    medicines.append(
                        Medicine(
                            medicine_id=row['medicine_id'],
                            name=row['name'],
                            manufacturer=row['manufacturer'],
                            description=row['description'],
                            price=row['price'],
                            stock_quantity=row['stock_quantity'],
                            expiry_date=str(row['expiry_date']),
                            created_at=row['created_at']
                        )
                    )
        except Exception as e:
            print(f"\n[Database Error] Failed to fetch medicines: {e}")
        return medicines
