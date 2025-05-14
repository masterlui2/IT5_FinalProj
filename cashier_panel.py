import tkinter as tk
from tkinter import ttk, messagebox
from db import get_db_connection
from decimal import Decimal
from tkinter import PhotoImage
from PIL import Image, ImageTk

class CashierPanel(tk.Frame):
    def __init__(self, master, switch_frame_callback, current_user_id):
        super().__init__(master, width=800, height=500)
        self.switch_frame = switch_frame_callback
        self.current_user_id = current_user_id
        self.pack_propagate(False)
        self.current_active_button = None  # Track active button

        self.hardware_categories = ['All', 'CPU', 'RAM', 'Motherboard', 'GPU', 'SSD', 'HDD', 'PSU', 'Case', 'Cooler']
        self.selected_product = None
        self.cart_items = {}

        # Configure styles
        self.configure_styles()

        # Create side panel
        self.create_side_panel()

        # Main content area
        self.content_frame = ttk.Frame(self, width=600, height=500)
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.content_frame.pack_propagate(False)

        # Set transaction as default view
        self.new_transaction()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("Selected.TButton", background="#90ee90", foreground="black")
        style.configure("Active.TButton", background="#4CAF50", foreground="white")
        style.configure("Regular.TButton", background="#f0f0f0", foreground="black")
        style.configure("Summary.TLabel", font=("Arial", 12))
        style.configure("Total.TLabel", font=("Arial", 12, "bold"))
        style.configure("Product.TFrame", padding=5)
        style.configure("AddCart.TButton", padding=2)
    # INSERT THE NEW METHOD RIGHT HERE (after configure_styles, before create_side_panel)
    def get_hardware_products(self, category="All"):
        """Fetch products from database based on category filter"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            if category == "All":
                cursor.execute("""
                    SELECT product_id, name, price, stock_quantity, category 
                    FROM products 
                    WHERE stock_quantity > 0
                    ORDER BY name
                """)
            else:
                cursor.execute("""
                    SELECT product_id, name, price, stock_quantity, category 
                    FROM products 
                    WHERE category = %s AND stock_quantity > 0
                    ORDER BY name
                """, (category,))
            
            products = cursor.fetchall()
            return products
        except Exception as e:
            print("Database error:", e)
            return []
        finally:
            conn.close()
    def create_side_panel(self):  # 🟩 This should be indented like this!
        side_panel = ttk.Frame(self, width=200, style="Side.TFrame")
        side_panel.pack(side="left", fill="y")
        side_panel.pack_propagate(False)

        # Image at top
        try:
            img = Image.open("i1.png")        # Replace with your image
            img = img.resize((180, 55))       # Match same size as menu header
            self.cashier_img = ImageTk.PhotoImage(img)
            tk.Label(side_panel, image=self.cashier_img, borderwidth=0).pack(pady=(10, 0))
        except Exception as e:
            print("Image load error:", e)

        self.transaction_btn = ttk.Button(
            side_panel, 
            text="Transaction", 
            command=lambda: self.switch_view(self.new_transaction, self.transaction_btn),
            style="Active.TButton"
        )
        self.transaction_btn.pack(pady=5, fill="x", padx=10)

        self.history_btn = ttk.Button(
            side_panel, 
            text="Transaction History", 
            command=lambda: self.switch_view(self.transaction_history, self.history_btn)
        )
        self.history_btn.pack(pady=5, fill="x", padx=10)

        ttk.Button(
            side_panel, 
            text="Logout", 
            command=lambda: self.switch_frame("login")
        ).pack(pady=30, fill="x", padx=10)

        self.current_active_button = self.transaction_btn



    def switch_view(self, view_func, button):
        """Switch between views and update active button styling"""
        if self.current_active_button:
            self.current_active_button.config(style="Regular.TButton")
        button.config(style="Active.TButton")
        self.current_active_button = button
        view_func()

    def new_transaction(self, filter_category="All"):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.selected_product = None
        product_buttons = []

        # Category filter buttons
        button_frame_top = ttk.Frame(self.content_frame)
        button_frame_bottom = ttk.Frame(self.content_frame)
        button_frame_top.pack(pady=(10, 0))
        button_frame_bottom.pack(pady=(5, 10))

        for cat in self.hardware_categories[:5]:
            ttk.Button(button_frame_top, text=cat, command=lambda c=cat: self.new_transaction(c)).pack(side="left", padx=5)
        for cat in self.hardware_categories[5:]:
            ttk.Button(button_frame_bottom, text=cat, command=lambda c=cat: self.new_transaction(c)).pack(side="left", padx=5)

        ttk.Label(self.content_frame, text=f"{filter_category} Products", font=("Arial", 14, "bold")).pack()

        # Main product and cart area
        main_area = ttk.Frame(self.content_frame)
        main_area.pack(fill="both", expand=True)

        # Product list with scrollbar
        product_frame = ttk.Frame(main_area)
        product_frame.pack(side="left", fill="both", expand=True, padx=5)

        canvas = tk.Canvas(product_frame)
        scrollbar = ttk.Scrollbar(product_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cart section
        cart_frame = ttk.Frame(main_area, relief="solid", padding=10, style="Cart.TFrame")
        cart_frame.pack(side="right", fill="y", padx=5, pady=5)

        ttk.Label(cart_frame, text="Selected Items", font=("Arial", 12, "bold")).pack()
        self.cart_listbox = tk.Listbox(cart_frame, width=35, height=15)
        self.cart_listbox.pack(pady=5)
        self.cart_total_label = ttk.Label(cart_frame, text="Total: ₱0.00", font=("Arial", 11, "bold"))
        self.cart_total_label.pack(pady=5)

        # Only show Checkout button in cart section (removed Add to Cart button)
        ttk.Button(cart_frame, text="Checkout", command=self.checkout_prompt).pack(pady=10)

        self.selected_label = ttk.Label(cart_frame, text="No product selected", font=("Arial", 10))
        self.selected_label.pack(pady=5)

        # Load products
        products = self.get_hardware_products(filter_category)
        if not products:
            ttk.Label(scrollable_frame, text="No products found.", font=("Arial", 12)).pack(pady=10)
            return

        # Display products with Add to Cart buttons
        for index, product in enumerate(products):
            # Create a frame for each product
            product_frame = ttk.Frame(scrollable_frame, style="Product.TFrame", width=400)  # Set your desired width
            product_frame.grid(row=index, column=0, sticky="ew", padx=15, pady=6)
            product_frame.grid_propagate(False)  # Prevent frame from shrinking to fit contents

            # Product info
            info_frame = ttk.Frame(product_frame)
            info_frame.pack(side="left", fill="x", expand=True)
            
            ttk.Label(info_frame, text=product['name'], font=("Arial", 10, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"₱{product['price']:.2f} | Stock: {product['stock_quantity']}").pack(anchor="w")
            
            # Add to Cart button
            add_button = ttk.Button(
                product_frame, 
                text="Add to Cart", 
                style="AddCart.TButton",
                command=lambda p=product: self.add_product_to_cart(p)
            )
            add_button.pack(side="right", padx=5)

    def add_product_to_cart(self, product):
        """Add a product directly to cart (called from product buttons)"""
        pid = product['product_id']
        current_stock = product['stock_quantity']
        
        if pid in self.cart_items:
            if self.cart_items[pid]['quantity'] >= current_stock:
                messagebox.showwarning("Stock Limit", f"Only {current_stock} items available in stock.")
                return
            self.cart_items[pid]['quantity'] += 1
        else:
            if current_stock < 1:
                messagebox.showwarning("Out of Stock", "This product is out of stock.")
                return
            self.cart_items[pid] = {
                'product': product, 
                'quantity': 1
            }
        
        self.refresh_cart_display()
        messagebox.showinfo("Added", f"{product['name']} added to cart")

    def checkout_prompt(self):
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Your cart is empty. Please add items first.")
            return

        popup = tk.Toplevel(self)
        popup.title("Checkout")
        popup.geometry("500x500")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        # Center the popup on screen
        self.center_window(popup)

        # Main container with padding
        container = ttk.Frame(popup, padding=20)
        container.pack(fill="both", expand=True)

        # Order summary title
        ttk.Label(container, text="Order Summary", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        # Scrollable order items
        canvas_frame = ttk.Frame(container)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, height=200, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Calculate total and display items
        total = Decimal("0.00")
        for item in self.cart_items.values():
            p = item['product']
            qty = item['quantity']
            price = Decimal(str(p['price'])) * qty
            total += price
            
            item_frame = ttk.Frame(scrollable_frame, padding=5)
            item_frame.pack(fill="x", pady=2)
            
            ttk.Label(item_frame, text=f"{p['name']} x{qty}", style="Summary.TLabel").pack(side="left")
            ttk.Label(item_frame, text=f"₱{price:.2f}", style="Summary.TLabel").pack(side="right")

        # Total amount
        ttk.Separator(container).pack(fill="x", pady=10)
        ttk.Label(container, text=f"Total Amount: ₱{total:.2f}", style="Total.TLabel").pack()

        # Payment section
        payment_frame = ttk.Frame(container, padding=(0, 15))
        payment_frame.pack()

        ttk.Label(payment_frame, text="Payment Amount:", style="Summary.TLabel").grid(row=0, column=0, padx=5, sticky="e")
        payment_entry = ttk.Entry(payment_frame, width=15, font=("Arial", 12))
        payment_entry.grid(row=0, column=1, padx=5)
        payment_entry.focus_set()

        # Change display
        change_frame = ttk.Frame(container)
        change_frame.pack(pady=10)
        ttk.Label(change_frame, text="Change:", style="Summary.TLabel").pack(side="left")
        self.change_label = ttk.Label(change_frame, text="₱0.00", style="Total.TLabel")
        self.change_label.pack(side="left")

        # Calculate change in real-time
        def calculate_change(*args):
            try:
                payment = Decimal(payment_entry.get())
                change = payment - total
                if change >= 0:
                    self.change_label.config(text=f"₱{change:.2f}", foreground="green")
                else:
                    self.change_label.config(text=f"(₱{-change:.2f} needed)", foreground="red")
            except Exception:
                self.change_label.config(text="Invalid amount", foreground="red")

        payment_entry.bind("<KeyRelease>", calculate_change)

        # Action buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=(15, 0))
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=popup.destroy,
            style="Regular.TButton"
        ).pack(side="left", padx=10)
        
        ttk.Button(
            button_frame, 
            text="Confirm Payment", 
            command=lambda: self.process_payment(popup, payment_entry, total),
            style="Active.TButton"
        ).pack(side="right", padx=10)

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def refresh_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        total = 0
        for item in self.cart_items.values():
            p = item['product']
            qty = item['quantity']
            line = f"{p['name']} x{qty} - ₱{p['price'] * qty:.2f}"
            self.cart_listbox.insert(tk.END, line)
            total += p['price'] * qty
        self.cart_total_label.config(text=f"Total: ₱{total:.2f}")

    def process_payment(self, popup, payment_entry, total):
        try:
            payment = Decimal(payment_entry.get())
            if payment < total:
                messagebox.showerror("Payment Error", "Payment amount is insufficient.")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            # Record transaction
            cursor.execute(
                "INSERT INTO transactions (user_id, total_amount, payment_amount, change_amount, transaction_date) "
                "VALUES (%s, %s, %s, %s, NOW())",
                (self.current_user_id, float(total), float(payment), float(payment - total))
            )
            transaction_id = cursor.lastrowid

            # Record transaction items and update stock
            for item in self.cart_items.values():
                p = item['product']
                qty = item['quantity']
                
                cursor.execute(
                    "INSERT INTO transaction_items (transaction_id, product_id, quantity, unit_price) "
                    "VALUES (%s, %s, %s, %s)",
                    (transaction_id, p['product_id'], qty, float(p['price']))
                )
                
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s "
                    "WHERE product_id = %s",
                    (qty, p['product_id'])
                )

            conn.commit()
            conn.close()

            # Clear cart and close popup
            self.cart_items.clear()
            self.refresh_cart_display()
            popup.destroy()
            messagebox.showinfo("Success", "Transaction completed successfully.")
            self.new_transaction()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid payment amount.")
        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {str(e)}")

    def transaction_history(self):
        """Display transaction history for the current user"""
        # Clear existing widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.content_frame, text="Transaction History", font=("Arial", 14, "bold")).pack(pady=10)

            # Create main container
        container = ttk.Frame(self.content_frame)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # Create frame for Treeview and scrollbars
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill="both", expand=True)

        # Create vertical scrollbar
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        
        # Create horizontal scrollbar
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Create Treeview with both scrollbars
        tree = ttk.Treeview(
            tree_frame,
            columns=("Transaction ID", "User ID", "Date", "Total", "Payment", "Change"),
            show="headings",
            height=15,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        # Configure column headings and widths
        columns = {
            "Transaction ID": 100,
            "User ID": 80,
            "Date": 150,
            "Total": 120,
            "Payment": 120,
            "Change": 120
        }

        for col, width in columns.items():
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        # Grid layout for Treeview and scrollbars
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        # Configure scrollbars
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)

        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        try:
            # Fetch data from database
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT transaction_id, user_id, total_amount, payment_amount, 
                       change_amount, transaction_date
                FROM transactions
                WHERE user_id = %s
                ORDER BY transaction_date DESC
            """, (self.current_user_id,))
            transactions = cursor.fetchall()
            conn.close()

            # Populate the treeview
            for txn in transactions:
                tree.insert("", "end", values=(
                    txn["transaction_id"],
                    txn["user_id"],
                    txn["transaction_date"].strftime("%Y-%m-%d %H:%M"),
                    f"₱{txn['total_amount']:.2f}",
                    f"₱{txn['payment_amount']:.2f}",
                    f"₱{txn['change_amount']:.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions.\n{e}")

    def get_hardware_products(self, filter_category="All"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            categories = ['CPU', 'RAM', 'Motherboard', 'GPU', 'SSD', 'HDD', 'PSU', 'Case', 'Cooler']
            if filter_category == "All":
                placeholders = ', '.join(['%s'] * len(categories))
                query = f"SELECT * FROM products WHERE category IN ({placeholders})"
                cursor.execute(query, categories)
            else:
                query = "SELECT * FROM products WHERE category = %s"
                cursor.execute(query, (filter_category,))
            products = cursor.fetchall()
            conn.close()
            return products
        except Exception as e:
            print("Database error:", e)
            return []