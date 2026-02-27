import customtkinter as ctk
from PIL import Image
from user_service import login
import config
from views import LoginScreen, AdminDashboard

# 1. Setup our Scalable Route Map
ROLE_FRAME_MAP = {
    'ADMINISTRATOR': AdminDashboard,
    'MANAGER': AdminDashboard, # Can map multiple roles to the same dashboard
    # 'TENANT': TenantDashboard, # Uncomment as you build them
}

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        # Save these to 'self' so other methods can access them!
        self.screen_width: int = self.winfo_screenwidth()
        self.screen_height: int = self.winfo_screenheight()
        
        self.geometry(f"{int(self.screen_width*config.WINDOW_SCALE)}x{int(self.screen_height*config.WINDOW_SCALE)}")
        self.after(1, self.wm_state, "zoomed")
        self.title(config.APP_TITLE)
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        # Initialize the state variable
        self.current_frame = None
        
        # Start the app!
        self.show_login_screen()
        
    def show_login_screen(self):
        # Clear the window if something else is there
        if self.current_frame:
            self.current_frame.destroy()
            
        # Instantiate your new LoginScreen class
        # Pass `self.handle_login` as the callback
        self.current_frame = LoginScreen(
            parent=self, 
            screen_width=self.screen_width, 
            screen_height=self.screen_height, 
            on_login_attempt=self.handle_login 
        )
        self.current_frame.pack(fill="both", expand=True)

    # Notice how we accept email and password as arguments here now!
    def handle_login(self, email: str, password: str) -> None:
        """ Processes the login attempt passed up from the LoginScreen. """
        
        # Call your service layer
        user = login(email, password)
        
        if user is None:
            # Tell the LoginScreen to show the error
            self.current_frame.show_error("Invalid email or password.")
        else:
            # Success
            print(f"Successfully logged in as {user.full_name}!")
            
            # Route them to the correct dashboard
            self.show_dashboard(user)

    def show_dashboard(self, user) -> None:
        """
        The scalable router. Destroys the login screen and loads the 
        correct dashboard based on the user's role.
        """
        # Clear the login screen
        if self.current_frame:
            self.current_frame.destroy()
            
        # Determine the user's role (assuming your user_service returns this!)
        # If it doesn't have a role, we'll default to TENANT
        user_role = getattr(user, 'role', 'TENANT')
        
        # Look up the correct frame class. Default to AdminDashboard for now 
        # so you don't crash while testing if the role is missing.
        FrameClass = ROLE_FRAME_MAP.get(user_role, AdminDashboard)
        
        # Instantiate the correct dashboard and pack it
        self.current_frame = FrameClass(parent=self, user=user)
        self.current_frame.pack(fill="both", expand=True)


def initialise() -> None:
    app = App()
    app.mainloop()