import tkinter as tk
from tkinter import ttk, messagebox
from db import get_db_connection

class SupplierManagementFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        columns = ("ID", "Name", "Email", "Phone")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=150)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, pady=10)
        ttk.Button(btn_frame, text="Add Supplier", command=self.open_add_form).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit Supplier", command=self.open_edit_form).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Supplier", command=self.delete_supplier).pack(side='left', padx=5)

        self.load_suppliers()

    def load_suppliers(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_id, name, email, phone FROM suppliers")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

    def open_add_form(self):
        self.open_form("Add Supplier")

    def open_edit_form(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Supplier", "Please select a supplier to edit.")
            return
        data = self.tree.item(selected[0])['values']
        self.open_form("Edit Supplier", data)

    def open_form(self, title, data=None):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("350x250")
        win.transient(self)
        win.grab_set()

        fields = [("Name", "name"), ("Email", "email"), ("Phone", "phone")]
        entries = {}

        for i, (label, key) in enumerate(fields):
            ttk.Label(win, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ttk.Entry(win, width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[key] = entry

        if data:
            entries["name"].insert(0, data[1])
            entries["email"].insert(0, data[2])
            entries["phone"].insert(0, data[3])

        def submit():
            name = entries["name"].get().strip()
            email = entries["email"].get().strip()
            phone = entries["phone"].get().strip()

            if not name or not email or not phone:
                messagebox.showerror("Error", "All fields are required.")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            if data:
                cursor.execute("""
                    UPDATE suppliers SET name=%s, email=%s, phone=%s WHERE supplier_id=%s
                """, (name, email, phone, data[0]))
            else:
                cursor.execute("""
                    INSERT INTO suppliers (name, email, phone) VALUES (%s, %s, %s)
                """, (name, email, phone))

            conn.commit()
            conn.close()
            win.destroy()
            self.load_suppliers()

        ttk.Button(win, text="Submit", command=submit).grid(row=len(fields), column=0, columnspan=2, pady=15)

    def delete_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier to delete.")
            return

        item = self.tree.item(selected[0])
        supplier_id = item["values"][0]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id = %s", (supplier_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            messagebox.showwarning("Cannot Delete", "Supplier has products linked. Remove them first.")
            conn.close()
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this supplier?"):
            cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
            conn.commit()

        conn.close()
        self.load_suppliers()
