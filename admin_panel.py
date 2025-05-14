import tkinter as tk
from tkinter import ttk
from user_management import UserManagementFrame
from product_management import ProductManagementFrame
from sales_report import show_sales_report
from financial_report import show_financial_report
from supplier_management import SupplierManagementFrame
from PIL import Image, ImageTk  # For better image handling

class AdminPanel(tk.Frame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.switch_frame_callback = switch_frame_callback
        self.configure(bg="white")
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar - slim and clean
        sidebar = ttk.Frame(self, width=200, padding=(0, 15, 0, 15), style="Sidebar.TFrame")
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)  # Prevent resizing
        sidebar.grid_rowconfigure(7, weight=1)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Sidebar.TFrame", background="black")
        
        # Menu buttons style
        self.style.configure("Menu.TButton", 
                           font=("Segoe UI", 10),
                           padding=6,
                           background="white",
                           foreground="black",
                           width=18,
                           relief="flat",
                           borderwidth=1)
        self.style.map("Menu.TButton",
                      background=[("active", "#e0e0e0")])
        
        # Active button style
        self.style.configure("Active.TButton",
                           background="#e0e0e0",
                           foreground="black",
                           bordercolor="black")
        
        # Logout button style
        self.style.configure("Logout.TButton",
                           background="black",
                           foreground="white",
                           bordercolor="white")
        self.style.map("Logout.TButton",
                      background=[("active", "#333333")])
        
        # Menu header with properly sized image
        menu_header = tk.Frame(sidebar, bg="black", height=60, pady=10)
        menu_header.pack(fill="x", pady=(0, 10))
        
        try:
            # Load and resize image to fit sidebar
            img = Image.open("i1.png")
            img = img.resize((160, 55))  # Adjusted to fit slim sidebar
            self.menu_img = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(menu_header,
                               image=self.menu_img,
                               bg="black",
                               borderwidth=0)
            img_label.pack()
        except Exception as e:
            print(f"Image error: {e}")
            # Clean fallback text
            tk.Label(menu_header,
                    text="ADMIN",
                    font=("Segoe UI", 12),
                    fg="white",
                    bg="black").pack()
        
        # Menu buttons
        self.menu_buttons = {}
        menu_items = [
            ("Products", lambda: self.show_section("Products")),
            ("Users", lambda: self.show_section("Users")),
            ("Suppliers", lambda: self.show_section("Suppliers")),
            ("Sales", lambda: self.show_section("Sales")),
            ("Financial", lambda: self.show_section("Financial"))
        ]
        
        for text, command in menu_items:
            btn = ttk.Button(sidebar,
                           text=text,
                           command=command,
                           style="Menu.TButton")
            btn.pack(fill="x", padx=10, pady=3, ipady=4)
            self.menu_buttons[text] = btn
        
        # Logout button
        ttk.Button(sidebar,
                  text="Logout",
                  command=lambda: self.switch_frame_callback("login"),
                  style="Logout.TButton").pack(fill="x", padx=10, pady=(15, 0), ipady=4)
        
        # Content area
        self.content = tk.Frame(self, bg="white", padx=20, pady=20)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.current_section = None
        
        # Default section
        self.show_section("Products")
        self.highlight_button("Products")

    def highlight_button(self, section_name):
        for btn in self.menu_buttons.values():
            btn.configure(style="Menu.TButton")
        if section_name in self.menu_buttons:
            self.menu_buttons[section_name].configure(style="Active.TButton")

    def show_section(self, section_name):
        self.highlight_button(section_name)
        
        # Clear current content
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Section label
        ttk.Label(self.content, 
                text=section_name, 
                font=("Segoe UI", 16),
                background="white").pack(pady=20)
        
        # Load section
        section_map = {
            "Users": UserManagementFrame,
            "Products": ProductManagementFrame,
            "Sales": show_sales_report,
            "Financial": show_financial_report,
            "Suppliers": SupplierManagementFrame
        }
        
        if section_name in section_map:
            self.current_section = section_map[section_name](self.content)
            if self.current_section:
                self.current_section.pack(fill='both', expand=True, padx=10, pady=10)