from tkinter import ttk, messagebox
from db import get_db_connection

def show_sales_report(parent):
    ttk.Label(parent, text="Sales Report", font=("Arial", 16, "bold")).pack(pady=10)

    tree = ttk.Treeview(parent, columns=("Product", "Qty Sold", "Total Sales"), show="headings")
    tree.heading("Product", text="Product")
    tree.heading("Qty Sold", text="Quantity Sold")
    tree.heading("Total Sales", text="Total Sales (₱)")
    tree.column("Product", width=200)
    tree.column("Qty Sold", width=120, anchor="center")
    tree.column("Total Sales", width=150, anchor="e")
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, SUM(ti.quantity) AS qty_sold, SUM(ti.quantity * ti.unit_price) AS total
            FROM transaction_items ti
            JOIN products p ON p.product_id = ti.product_id
            GROUP BY ti.product_id, p.name
            ORDER BY total DESC
        """)
        for row in cursor.fetchall():
            name, qty, total = row
            tree.insert("", "end", values=(name, qty, f"{total:.2f}"))
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load sales report.\n{e}")
