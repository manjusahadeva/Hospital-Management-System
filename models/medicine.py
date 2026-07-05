class Medicine:
    def __init__(self, name, price, stock_quantity, expiry_date, manufacturer=None, description=None, medicine_id=None, created_at=None):
        self.medicine_id = medicine_id
        self.name = name
        self.manufacturer = manufacturer
        self.description = description
        self.price = float(price)
        self.stock_quantity = int(stock_quantity)
        self.expiry_date = expiry_date  # YYYY-MM-DD
        self.created_at = created_at
    def __repr__(self):
        return f"Medicine(id={self.medicine_id}, name='{self.name}', price={self.price}, stock={self.stock_quantity})"
