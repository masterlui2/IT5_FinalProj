import tkinter as tk
from tkinter import ttk
from login_window import LoginWindow
from admin_panel import AdminPanel
from cashier_panel import CashierPanel

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("POS System")
        self.geometry("800x500")
        self.resizable(False, False)

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure(bg="#f5f5f5")

        # Frame management
        self.active_frame = None
        self.switch_frame("login")

    def switch_frame(self, target, **kwargs):
        if self.active_frame:
            self.active_frame.destroy()

        if target == "login":
            self.active_frame = LoginWindow(self, self.switch_frame)
        elif target == "admin":
            self.active_frame = AdminPanel(self, self.switch_frame)
        elif target == "cashier":
            user_id = kwargs.get("user_id")
            self.active_frame = CashierPanel(self, self.switch_frame, current_user_id=user_id)

        self.active_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = App()
    app.mainloop()