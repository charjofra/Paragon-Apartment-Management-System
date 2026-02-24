from customtkinter import *
from PIL import Image
from user_service import login
import config

class App(CTk):
    def __init__(self) -> None:
        super().__init__()
        
        SCREEN_WIDTH: int = self.winfo_screenwidth()
        SCREEN_HEIGHT: int = self.winfo_screenheight()
        
        self.geometry(f"{int(SCREEN_WIDTH*config.WINDOW_SCALE)}x{int(SCREEN_HEIGHT*config.WINDOW_SCALE)}")
        self.after(1, self.wm_state, "zoomed")
        self.title(config.APP_TITLE)
        set_appearance_mode(config.APPEARANCE_MODE)
        set_default_color_theme(config.COLOR_THEME)
        
        self.login_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        
    def login_screen(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int) -> None:
        login_background = CTkImage(light_image=Image.open(config.LOGIN_BG_IMAGE), dark_image=Image.open(config.LOGIN_BG_IMAGE), size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        background_label = CTkLabel(master=self, text="", image=login_background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.login_frame = CTkFrame(master=self, fg_color=("#ffffff", "#2b2b2b"), border_width=0)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Left side (branding)
        branding_frame = CTkFrame(master=self.login_frame, fg_color="#1f538d", width=350, height=550)
        branding_frame.pack(side="left", fill="y", padx=0, pady=0)
        branding_frame.pack_propagate(False)
        
        logo_label = CTkLabel(master=branding_frame, text="PARAGON", font=("Helvetica", 45, "bold"), text_color="white")
        logo_label.pack(pady=(180, 10))
        
        sub_logo = CTkLabel(master=branding_frame, text="Apartment Management\nSystem", font=("Helvetica", 20), text_color="#d0d0d0", justify="center")
        sub_logo.pack()
        
        # Right side (login form)
        form_frame = CTkFrame(master=self.login_frame, fg_color="transparent", width=450, height=550)
        form_frame.pack(side="right", fill="both", expand=True, padx=50, pady=50)
        
        login_label = CTkLabel(master=form_frame, text="Welcome Back", font=("Helvetica", 36, "bold"))
        login_label.pack(anchor="w", pady=(20, 5))
        
        subtitle = CTkLabel(master=form_frame, text="Please enter your details to sign in.", font=("Helvetica", 16), text_color="gray")
        subtitle.pack(anchor="w", pady=(0, 40))
        
        email_label = CTkLabel(master=form_frame, text="Email address", font=("Helvetica", 15, "bold"))
        email_label.pack(anchor="w", pady=(10, 5))
        
        self.email_entry = CTkEntry(master=form_frame, placeholder_text="example@email.com", font=("Helvetica", 15), width=350, height=50, border_width=1)
        self.email_entry.pack(anchor="w", pady=(0, 20))
        
        password_label = CTkLabel(master=form_frame, text="Password", font=("Helvetica", 15, "bold"))
        password_label.pack(anchor="w", pady=(10, 5))
        
        self.password_entry = CTkEntry(master=form_frame, placeholder_text="Enter your password", font=("Helvetica", 15), show="*", width=350, height=50, border_width=1)
        self.password_entry.pack(anchor="w", pady=(0, 20))

        self.error_label = CTkLabel(master=form_frame, text="", text_color="#ff4c4c", font=("Helvetica", 14))
        self.error_label.pack(anchor="w", pady=(5, 0))
        
        login_button = CTkButton(master=form_frame, text="Log In", font=("Helvetica", 18, "bold"), width=350, height=50, fg_color="#1f538d", hover_color="#14375e", command=self.handle_login)
        login_button.pack(anchor="w", pady=(20, 20))

    def handle_login(self) -> None:
        """ Processes the login attempt and updates the GUI. """
        
        # Clear previous errors
        self.error_label.configure(text="") 
        
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        # Call the service layer
        user = login(email, password)
        
        if user is None:
            # Show error to the user
            self.error_label.configure(text="Invalid email or password.")
        else:
            # Success
            print(f"Successfully logged in as {user.full_name}!")
            
            # Hide/destroy the login frame and load the main app
            self.login_frame.destroy()
            self.dashboard(user)

    def dashboard(self, user) -> None:
        """
        The main home screen of the app.
        This is where the user goes after a successful login.
        """
        
        welcome_label = CTkLabel(master=self, text=f"Welcome, {user.full_name}!", font=("Arial", 40))
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")

def initialise() -> None:
    app = App()
    app.mainloop()