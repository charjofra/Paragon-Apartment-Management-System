import customtkinter as ctk
import config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui import App

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent: "App", screen_width: int, screen_height: int, on_login_attempt):
        # Initialize the frame to take up the whole screen
        super().__init__(parent, corner_radius=0)
        
        self.on_login_attempt = on_login_attempt
        
        # 1. Full-screen Background
        self.background_label = ctk.CTkLabel(self, text="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 2. Centered Inner Form Container
        self.inner_frame = ctk.CTkFrame(self, border_width=0)
        self.inner_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # 3. Left side (branding)
        branding_frame = ctk.CTkFrame(self.inner_frame, fg_color=("#D5D5D4", "#353535"), width=350, height=550)
        branding_frame.pack(side="left", fill="y", padx=0, pady=0)
        branding_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(branding_frame, text="PARAGON", font=("Helvetica Neue", 45, "bold"))
        logo_label.pack(pady=(180, 10))
        
        sub_logo = ctk.CTkLabel(branding_frame, text="Apartment Management\nSystem", font=("Helvetica Neue", 20), justify="center")
        sub_logo.pack()
        
        # 4. Right side (login form)
        form_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent", width=450, height=550)
        form_frame.pack(side="right", fill="both", expand=True, padx=50, pady=50)
        
        login_label = ctk.CTkLabel(form_frame, text="Welcome Back", font=("Helvetica Neue", 36, "bold"))
        login_label.pack(anchor="w", pady=(20, 5))
        
        subtitle = ctk.CTkLabel(form_frame, text="Please enter your details to sign in.", font=("Helvetica Neue", 16))
        subtitle.pack(anchor="w", pady=(0, 40))
        
        email_label = ctk.CTkLabel(form_frame, text="Email address", font=("Helvetica Neue", 15, "bold"))
        email_label.pack(anchor="w", pady=(10, 5))
        
        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="example@email.com", font=("Helvetica Neue", 15), width=350, height=50, border_width=1)
        self.email_entry.pack(anchor="w", pady=(0, 20))
        
        password_label = ctk.CTkLabel(form_frame, text="Password", font=("Helvetica Neue", 15, "bold"))
        password_label.pack(anchor="w", pady=(10, 5))
        
        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your password", font=("Helvetica Neue", 15), show="*", width=350, height=50, border_width=1)
        self.password_entry.pack(anchor="w", pady=(0, 20))

        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="#ff4c4c", font=("Helvetica Neue", 14))
        self.error_label.pack(anchor="w", pady=(5, 0))
        
        # Bind the button to the internal method
        login_button = ctk.CTkButton(form_frame, text="Log In", font=("Helvetica Neue", 18, "bold"), width=350, height=50, command=self._handle_click)
        login_button.pack(anchor="w", pady=(20, 20))

    def _handle_click(self):
        """Internal method to grab input values and trigger the callback."""
        # Clear previous errors
        self.show_error("") 
        
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        # Pass data back to the main App controller
        self.on_login_attempt(email, password)

    def show_error(self, message: str):
        """Public method so the main App can update the UI if login fails."""
        self.error_label.configure(text=message)