import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from db import get_db_connection

class UserManagementFrame(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=20)
        self.tree = None
        self.build_ui()
        self.load_users()
        master.winfo_toplevel().minsize(700, 400)

    def build_ui(self):
        ttk.Label(self, text="User Management", font=("Arial", 16)).pack(pady=10)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')

        # Treeview without "Role" column
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Username", "Full Name", "Status"), show='headings', yscrollcommand=tree_scroll.set)
        for col, width in [("ID", 50), ("Username", 140), ("Full Name", 220), ("Status", 100)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        self.tree.pack(fill='both', expand=True)
        tree_scroll.config(command=self.tree.yview)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Add User", command=lambda: self.open_user_form(False)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit User", command=lambda: self.open_user_form(True)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Remove User", command=self.remove_user).pack(side='left', padx=5)

    def load_users(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, full_name, status, role FROM users WHERE role != 'admin'")
        for row in cursor.fetchall():
            # Insert only ID, Username, Full Name, and Status into the table (omit role)
            self.tree.insert('', 'end', values=row[:4])
        conn.close()

    def remove_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a user to remove.")
            return
        user = self.tree.item(selected[0])['values']
        if user[3].lower() == 'active':
            messagebox.showerror("Cannot Remove", "Cannot remove an active user. Please set status to 'Inactive' first.")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user[0],))
        conn.commit()
        conn.close()
        self.load_users()

    def open_user_form(self, edit=False):
        form = tk.Toplevel(self)
        form.title("Edit User" if edit else "Add User")
        form.geometry("350x400")
        form.grab_set()

        form.update_idletasks()
        x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)
        y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2)
        form.geometry(f"+{x}+{y}")

        tk.Label(form, text="Username:").pack(pady=(10, 0))
        username_entry = tk.Entry(form)
        username_entry.pack()

        tk.Label(form, text="Password (hashed):").pack(pady=(10, 0))
        password_entry = tk.Entry(form)
        password_entry.pack()

        tk.Label(form, text="Full Name:").pack(pady=(10, 0))
        full_name_entry = tk.Entry(form)
        full_name_entry.pack()

        status_var = tk.StringVar(value="active")
        tk.Label(form, text="Status:").pack(pady=(10, 0))
        status_frame = ttk.Frame(form)
        status_frame.pack()
        tk.Radiobutton(status_frame, text="Active", variable=status_var, value="active").pack(side='left', padx=10)
        tk.Radiobutton(status_frame, text="Inactive", variable=status_var, value="inactive").pack(side='left', padx=10)

        role_var = tk.StringVar(value="user")
        tk.Label(form, text="Role:").pack(pady=(10, 0))
        role_frame = ttk.Frame(form)
        role_frame.pack()
        tk.Radiobutton(role_frame, text="User", variable=role_var, value="user").pack(side='left', padx=10)
        tk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin").pack(side='left', padx=10)

        if edit:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("No selection", "Please select a user to edit.")
                form.destroy()
                return
            user = self.tree.item(selected[0])['values']
            username_entry.insert(0, user[1])
            full_name_entry.insert(0, user[2])
            status_var.set(user[3].lower())

            # Fetch role from DB for the selected user
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user[0],))
            role = cursor.fetchone()
            conn.close()
            if role:
                role_var.set(role[0].lower())

        def submit():
            username = username_entry.get().strip()
            full_name = full_name_entry.get().strip()
            status = status_var.get()
            role = role_var.get()

            if not username or not full_name:
                messagebox.showwarning("Missing Fields", "Username and Full Name are required.")
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                if edit:
                    user_id = self.tree.item(self.tree.selection()[0])['values'][0]
                    cursor.execute("UPDATE users SET username=%s, full_name=%s, status=%s, role=%s WHERE user_id=%s",
                                (username, full_name, status, role, user_id))
                else:
                    password = password_entry.get().strip()
                    if not password:
                        messagebox.showwarning("Missing Password", "Password is required for new users.")
                        return
                    cursor.execute("INSERT INTO users (username, password_hash, full_name, status, role) VALUES (%s, %s, %s, %s, %s)",
                                (username, password, full_name, status, role))

                conn.commit()
                conn.close()
                form.destroy()
                self.load_users()

            except Exception as e:
                conn.rollback()
                conn.close()

                retry = messagebox.askretrycancel("Database Error", f"An error occurred:\n{str(e)}\n\nWould you like to retry?")
                if retry:
                    return 
                else:
                    form.destroy()

        tk.Button(form, text="Submit", command=submit).pack(pady=20)
