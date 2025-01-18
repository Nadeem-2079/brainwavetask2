import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pandas as pd

def create_connection():
    return sqlite3.connect("inventory.db")

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        product_id INTEGER PRIMARY KEY,
                        product_name TEXT NOT NULL,
                        category TEXT,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                        sale_id INTEGER PRIMARY KEY,
                        product_id INTEGER,
                        quantity INTEGER,
                        total_price REAL,
                        sale_date TEXT,
                        FOREIGN KEY (product_id) REFERENCES inventory (product_id))''')
    
    conn.commit()
    conn.close()

create_tables()

def add_product(name, category, quantity, price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO inventory (product_name, category, quantity, price)
                      VALUES (?, ?, ?, ?)''', (name, category, quantity, price))
    conn.commit()
    conn.close()

def edit_product(product_id, name, category, quantity, price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE inventory SET product_name = ?, category = ?, quantity = ?, price = ?
                      WHERE product_id = ?''', (name, category, quantity, price, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM inventory WHERE product_id = ?''', (product_id,))
    conn.commit()
    conn.close()

def get_inventory():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM inventory''')
    inventory = cursor.fetchall()
    conn.close()
    return inventory

def record_sale(product_id, quantity):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''SELECT price, quantity FROM inventory WHERE product_id = ?''', (product_id,))
    product = cursor.fetchone()
    
    if not product or product[1] < quantity:
        print("Insufficient stock.")
        return
    
    price = product[0]
    total_price = price * quantity

    cursor.execute('''UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?''', (quantity, product_id))
    
    sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT INTO sales (product_id, quantity, total_price, sale_date)
                      VALUES (?, ?, ?, ?)''', (product_id, quantity, total_price, sale_date))
    
    conn.commit()
    conn.close()

def low_stock_alert(threshold=5):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT product_name, quantity FROM inventory WHERE quantity <= ?''', (threshold,))
    low_stock_items = cursor.fetchall()
    conn.close()
    return low_stock_items

def generate_sales_report():
    conn = create_connection()
    query = '''SELECT s.sale_id, i.product_name, s.quantity, s.total_price, s.sale_date
               FROM sales s JOIN inventory i ON s.product_id = i.product_id'''
    sales_data = pd.read_sql_query(query, conn)
    conn.close()
    return sales_data

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.create_widgets()
    
    def create_widgets(self):
        self.product_name_label = tk.Label(self.root, text="Product Name:")
        self.product_name_label.grid(row=0, column=0)
        self.product_name_entry = tk.Entry(self.root)
        self.product_name_entry.grid(row=0, column=1)
        
        self.category_label = tk.Label(self.root, text="Category:")
        self.category_label.grid(row=1, column=0)
        self.category_entry = tk.Entry(self.root)
        self.category_entry.grid(row=1, column=1)
        
        self.quantity_label = tk.Label(self.root, text="Quantity:")
        self.quantity_label.grid(row=2, column=0)
        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.grid(row=2, column=1)
        
        self.price_label = tk.Label(self.root, text="Price:")
        self.price_label.grid(row=3, column=0)
        self.price_entry = tk.Entry(self.root)
        self.price_entry.grid(row=3, column=1)
        
        self.add_button = tk.Button(self.root, text="Add Product", command=self.add_product)
        self.add_button.grid(row=4, column=0, columnspan=2)

        self.view_button = tk.Button(self.root, text="View Inventory", command=self.view_inventory)
        self.view_button.grid(row=5, column=0, columnspan=2)

        self.low_stock_button = tk.Button(self.root, text="Low Stock Alerts", command=self.view_low_stock)
        self.low_stock_button.grid(row=6, column=0, columnspan=2)
        
    def add_product(self):
        name = self.product_name_entry.get()
        category = self.category_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()
        
        # Input validation
        if not name or not category or not quantity or not price:
            messagebox.showerror("Error", "All fields must be filled!")
            return
        
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and price must be a float!")
            return
        
        # Add product to the database
        add_product(name, category, quantity, price)
        messagebox.showinfo("Success", "Product added successfully!")
        
        # Clear entries
        self.product_name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def view_inventory(self):
        inventory = get_inventory()
        inventory_str = "\n".join([f"{item[0]}: {item[1]} | {item[2]} | {item[3]} units | ${item[4]}" for item in inventory])
        messagebox.showinfo("Inventory", inventory_str)

    def view_low_stock(self):
        low_stock_items = low_stock_alert()
        if low_stock_items:
            low_stock_str = "\n".join([f"{item[0]}: {item[1]} units left" for item in low_stock_items])
            messagebox.showinfo("Low Stock Alerts", low_stock_str)
        else:
            messagebox.showinfo("Low Stock Alerts", "No products are low on stock!")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


