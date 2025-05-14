from tkinter import ttk, messagebox
from db import get_db_connection
from datetime import datetime

def show_financial_report(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    ttk.Label(parent, text="📊 Financial Report", font=("Arial", 18, "bold")).pack(pady=15)

    container = ttk.Frame(parent, padding=20, relief="ridge")
    container.pack(padx=20, pady=10, fill="x")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get general financial data
        cursor.execute("""
            SELECT COUNT(*) AS num_txn,
                   SUM(total_amount),
                   SUM(payment_amount),
                   SUM(change_amount)
            FROM transactions
        """)
        txn_result = cursor.fetchone()

        total_txn = txn_result[0] or 0
        total_sales = txn_result[1] or 0
        total_received = txn_result[2] or 0
        total_change = txn_result[3] or 0

        # Get total manufacturing price of sold products
        cursor.execute("""
            SELECT SUM(COALESCE(p.manufacturing_price, 0) * COALESCE(si.quantity, 0)) AS total_manufacturing_price
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
        """)
        manufacturing_result = cursor.fetchone()
        total_manufacturing_price = manufacturing_result[0] or 0

        # Get total units sold
        cursor.execute("SELECT SUM(quantity) FROM sale_items")
        quantity_result = cursor.fetchone()
        total_units_sold = quantity_result[0] or 0

        conn.close()

        # Net income calculation (excluding change)
        net_income = total_sales - total_manufacturing_price

        metrics = [
            ("🧾 Total Transactions", total_txn, "#4a90e2"),
            ("📦 Units Sold", total_units_sold, "#1abc9c"),
            ("🏷️ Total Manufacturing Cost", f"₱{total_manufacturing_price:,.2f}", "#ff6348"),
            ("💵 Total Sales", f"₱{total_sales:,.2f}", "#7ed6df"),
            ("💰 Total Received", f"₱{total_received:,.2f}", "#70a1ff"),
            ("🎁 Total Change Given", f"₱{total_change:,.2f}", "#ffa502"),
            ("📈 Net Income", f"₱{net_income:,.2f}", "#2ed573")
        ]

        for i, (label, value, color) in enumerate(metrics):
            frame = ttk.Frame(container, padding=10)
            frame.grid(row=i, column=0, sticky="ew", pady=4)
            frame.columnconfigure(1, weight=1)

            ttk.Label(frame, text=label, font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
            val_lbl = ttk.Label(frame, text=value, font=("Arial", 12), background=color, foreground="white", padding=5)
            val_lbl.grid(row=0, column=1, sticky="e", padx=10)

        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        ttk.Label(parent, text=f"Generated on {timestamp}", font=("Arial", 9, "italic")).pack(pady=(5, 0))

    except Exception as e:
        messagebox.showerror("Error", f"Could not load financial report.\n{e}")
