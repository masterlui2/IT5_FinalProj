import tkinter as tk
from tkinter import ttk, messagebox
from db import get_db_connection

class ProductManagementFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        columns = ("ID", "Name", "Category", "Brand", "Price", "Manufacturing Price", "Stock", "Reorder", "Supplier ID")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=120)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, pady=10)
        ttk.Button(btn_frame, text="Add Product", command=self.open_add_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit Product", command=self.open_edit_product).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remove Product", command=self.remove_product).pack(side='left', padx=5)

        self.load_products()

    def load_products(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_id, name, category, brand, price, manufacturing_price, stock_quantity, reorder_level, supplier_id
            FROM products
        """)
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

    def open_add_product(self):
        self.open_product_form("Add Product")

    def open_edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to edit.")
            return
        product_data = self.tree.item(selected[0])['values']
        self.open_product_form("Edit Product", product_data)

    def open_product_form(self, title, product_data=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("450x500")
        form.grab_set()
        form.transient(self)

        form.update_idletasks()
        w = form.winfo_width()
        h = form.winfo_height()
        x = (form.winfo_screenwidth() // 2) - (w // 2)
        y = (form.winfo_screenheight() // 2) - (h // 2)
        form.geometry(f"+{x}+{y}")

        # --- Supplier Dropdown ---
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_id, name FROM suppliers ORDER BY name")
        suppliers = cursor.fetchall()
        conn.close()

        supplier_map = {name: sid for sid, name in suppliers}
        supplier_names = list(supplier_map.keys())

        ttk.Label(form, text="Supplier", width=15, anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(form, textvariable=supplier_var, values=supplier_names, state="readonly", width=28)
        supplier_combo.grid(row=0, column=1, padx=10, pady=5)

        # --- Form Fields ---
        entries = {}
        fields = [("Name", "name"), ("Category", "category"), ("Brand", "brand"),
                ("Description", "description"), ("Price", "price"), ("Manufacturing Price", "manufacturing_price"),
                ("Stock Quantity", "stock_quantity"), ("Reorder Level", "reorder_level")]

        stock_var = tk.IntVar(value=0)

        for i, (label_text, field) in enumerate(fields, start=1):  # Start at row 1
            ttk.Label(form, text=label_text, width=15, anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=5)

            if field == "description":
                desc_frame = ttk.Frame(form)
                desc_frame.grid(row=i, column=1, padx=11, pady=5, sticky="w")
                entry = tk.Text(desc_frame, height=2, width=30, wrap="word", font=("TkDefaultFont", 10))
                entry.pack(fill="x")
                entries[field] = entry
            elif field == "stock_quantity" and product_data:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (product_data[0],))
                result = cursor.fetchone()
                conn.close()
                if result:
                    stock_var.set(result[0])

                stock_frame = ttk.Frame(form)
                stock_frame.grid(row=i, column=1, padx=10, pady=5)

                def increase_stock():
                    stock_var.set(stock_var.get() + 1)

                def decrease_stock():
                    if stock_var.get() > 0:
                        stock_var.set(stock_var.get() - 1)

                ttk.Button(stock_frame, text="-", width=3, command=decrease_stock).pack(side="left")
                stock_entry = ttk.Entry(stock_frame, textvariable=stock_var, width=10, justify="center")
                stock_entry.pack(side="left", padx=5)
                ttk.Button(stock_frame, text="+", width=3, command=increase_stock).pack(side="left")

                entries[field] = stock_var
            else:
                entry = ttk.Entry(form, width=30)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[field] = entry

        if product_data:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT description, supplier_id, manufacturing_price FROM products WHERE product_id = %s", (product_data[0],))
            result = cursor.fetchone()
            description = result[0] if result else ""
            supplier_id = result[1] if result else None
            manufacturing_price = result[2] if result else ""
            conn.close()

            values_map = {
                "name": product_data[1], "category": product_data[2], "brand": product_data[3],
                "description": description, "price": product_data[4], "manufacturing_price": manufacturing_price,
                "reorder_level": product_data[6],
            }

            for key, entry in entries.items():
                if key == "description":
                    entry.insert("1.0", values_map.get(key, ""))
                elif key in values_map:
                    entry.delete(0, tk.END)
                    entry.insert(0, values_map[key])

            # Prefill supplier combo
            for name, sid in supplier_map.items():
                if sid == supplier_id:
                    supplier_var.set(name)
                    break

        def submit():
            try:
                for key in ["name", "category", "brand", "price", "manufacturing_price", "reorder_level"]:
                    value = entries[key].get().strip()
                    if not value:
                        raise ValueError("Please fill all fields.")

                if product_data:
                    stock = stock_var.get()
                else:
                    stock_str = entries["stock_quantity"].get().strip()
                    if not stock_str:
                        raise ValueError("Please fill all fields.")
                    stock = int(stock_str)

                price = float(entries["price"].get())
                manufacturing_price = float(entries["manufacturing_price"].get())
                reorder = int(entries["reorder_level"].get())

                selected_supplier = supplier_var.get()
                if not selected_supplier:
                    raise ValueError("Please select a supplier.")
                supplier_id = supplier_map.get(selected_supplier)

                values = {
                    "name": entries["name"].get().strip(),
                    "category": entries["category"].get().strip(),
                    "brand": entries["brand"].get().strip(),
                    "description": entries["description"].get("1.0", "end").strip(),
                    "price": price,
                    "manufacturing_price": manufacturing_price,
                    "stock_quantity": stock,
                    "reorder_level": reorder,
                    "supplier_id": supplier_id
                }

            except ValueError:
                messagebox.showerror("Invalid Input", "Please fill all fields and ensure numeric fields are valid.")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            if product_data:
                cursor.execute("""
                    UPDATE products SET name=%s, category=%s, brand=%s, description=%s,
                    price=%s, manufacturing_price=%s, stock_quantity=%s, reorder_level=%s, supplier_id=%s WHERE product_id=%s
                """, (
                    values["name"], values["category"], values["brand"], values["description"],
                    values["price"], values["manufacturing_price"], values["stock_quantity"], values["reorder_level"], values["supplier_id"],
                    product_data[0]
                ))
            else:
                cursor.execute("""
                    INSERT INTO products (name, category, brand, description, price, manufacturing_price, stock_quantity, reorder_level, supplier_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    values["name"], values["category"], values["brand"], values["description"],
                    values["price"], values["manufacturing_price"], values["stock_quantity"], values["reorder_level"], values["supplier_id"]
                ))

            conn.commit()
            conn.close()
            form.destroy()
            self.load_products()

        ttk.Button(form, text="Submit", command=submit).grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

    def remove_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product to remove.")
            return
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        stock_quantity = item['values'][5]
        if stock_quantity > 0:
            messagebox.showinfo("Cannot Delete", "Product stock must be zero before deletion.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            conn.commit()
            conn.close()
            self.load_products()
