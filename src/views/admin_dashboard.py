from customtkinter import *
from models.user import User
from gui import App

class AdminDashboard(CTkFrame):
    def __init__(self, parent: App, user: User):
        super().__init__(parent)
        label = CTkLabel(self, text=f"Admin Panel - Logged in as: {user.full_name}")
        label.pack(pady=20)