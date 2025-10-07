import json
import os
from datetime import datetime

DB_FILE = "database.json"

class Product:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.date_added = datetime.now().isoformat()

class Sale:
    def __init__(self, product_id, quantity_sold, total):
        self.product_id = product_id
        self.quantity_sold = quantity_sold
        self.total = total
        self.date = datetime.now().isoformat()

def load_data():
    if not os.path.exists(DB_FILE):
        return {"products": [], "sales": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
