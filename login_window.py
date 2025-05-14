import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db import get_db_connection

class LoginWindow(tk.Frame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.switch_frame = switch_frame_callback
        self.configure(bg="#f5f5f5")  # Match app background
        
        # Create a main container that holds both login and image frames
        main_container = tk.Frame(self, bg="#f5f5f5")
        main_container.pack(expand=True, fill="both", padx=15, pady=5)
        
        # Left side - Login container
        login_container = tk.Frame(main_container, bg="white", padx=40, pady=40)
        login_container.pack(side="left", fill="both", expand=True)
        
        # Load and display logo image (replace 'logo.png' with your image path)
        try:
            logo_img = Image.open("i1.png")
            logo_img = logo_img.resize((200, 100), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(login_container, image=self.logo, bg="white")
            logo_label.pack(pady=(0, 30))
        except:
            # Fallback if image not found
            logo_label = tk.Label(login_container, 
                                text="COMPANY LOGO", 
                                font=("Segoe UI", 16, "bold"),
                                bg="white",
                                pady=10)
            logo_label.pack(pady=(0, 30))
        
        # Username field
        username_frame = tk.Frame(login_container, bg="white")
        username_frame.pack(pady=(10, 10), fill="x")
        
        tk.Label(username_frame, 
                text="Username", 
                font=("Segoe UI", 10),
                bg="white").pack(anchor="center")
        
        self.entry_username = ttk.Entry(username_frame, width=25)
        self.entry_username.pack(pady=(5, 0))
        
        # Password field
        password_frame = tk.Frame(login_container, bg="white")
        password_frame.pack(pady=(15, 10), fill="x")
        
        tk.Label(password_frame, 
                text="Password", 
                font=("Segoe UI", 10),
                bg="white").pack(anchor="center")
        
        self.entry_password = ttk.Entry(password_frame, show="•", width=25)
        self.entry_password.pack(pady=(5, 0))
    
        # Modern sign in button with light green color
        self.style = ttk.Style()
        self.style.configure("Modern.TButton", 
                           font=("Segoe UI", 10, "bold"),
                           padding=10,
                           background="#8bc34a",  # Light green
                           foreground="green",
                           bordercolor="#8bc34a",
                           focuscolor="#8bc34a",
                           lightcolor="#8bc34a",
                           darkcolor="#689f38")  # Darker green for pressed state
        
        signin_btn = ttk.Button(login_container, 
                              text="Sign in", 
                              command=self.login,
                              style="Modern.TButton",
                              width=20)
        signin_btn.pack()
        
        # Right side - Image container
        image_container = tk.Frame(main_container, bg="#f5f5f5")
        image_container.pack(side="right", fill="both", expand=True)
        try:
            side_img = Image.open("bg.png")
            side_img = side_img.resize((400, 400), Image.LANCZOS)
            self.side_image = ImageTk.PhotoImage(side_img)
            side_label = tk.Label(image_container, image=self.side_image, bg="#f5f5f5")
            side_label.pack(expand=True, fill="both")
        except:
            # Fallback if image not found
            side_label = tk.Label(image_container, 
                                text="SIDE IMAGE", 
                                font=("Segoe UI", 16),
                                bg="#e0e0e0",
                                fg="gray")
            side_label.pack(expand=True, fill="both")
        
        # Focus on username field by default
        self.entry_username.focus()
    
    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        user = self.validate_login(username, password)
        if user:
            role = user['role'].lower()
            user_id = user['user_id']
            if role == 'admin':
                self.switch_frame("admin")
            else:
                self.switch_frame("cashier", user_id=user_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def validate_login(self, username, password):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and user['password_hash'] == password:
                return user
            return None
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return None
    
