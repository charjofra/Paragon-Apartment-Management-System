import customtkinter as ctk
from models.user import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui import App

class TenantDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text=f"Tenant Dashboard - Logged in as: {user.full_name}")
        label.pack(pady=20)