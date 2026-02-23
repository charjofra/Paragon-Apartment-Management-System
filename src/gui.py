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
        
        # Make the frame an instance variable so it can be destroyed later
        self.login_frame = CTkFrame(master=self)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        login_label = CTkLabel(master=self.login_frame, text="Login", font=("Arial", 50))
        login_label.grid(row=0, column=0, pady=30, sticky="n")
        
        input_frame = CTkFrame(master=self.login_frame, fg_color=("transparent"))
        input_frame.grid(row=1, column=0, padx=50)
        
        email_label = CTkLabel(master=input_frame, text="Email address", font=("Arial", 20))
        email_label.pack(anchor="w", pady=(15, 1))
        
        self.email_entry = CTkEntry(master=input_frame, placeholder_text="example@email.com", font=("Arial", 20), width=300, height=50)
        self.email_entry.pack(anchor="w", pady=(1, 15))
        
        password_label = CTkLabel(master=input_frame, text="Password", font=("Arial", 20))
        password_label.pack(anchor="w", pady=(15, 1))
        
        self.password_entry = CTkEntry(master=input_frame, placeholder_text="Please enter password", font=("Arial", 20), show="•", width=300, height=50)
        self.password_entry.pack(anchor="w", pady=(1, 15))

        # Hidden error label (only shows up if login fails)
        self.error_label = CTkLabel(master=self.login_frame, text="", text_color="red", font=("Arial", 14))
        self.error_label.grid(row=2, column=0)
        
        login_button = CTkButton(master=self.login_frame, text="Log In", font=("Arial", 30), width=200, height=50, command=self.handle_login)
        login_button.grid(row=3, column=0, pady=30)

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