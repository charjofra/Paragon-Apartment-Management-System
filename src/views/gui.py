import customtkinter as ctk
from services.user_service import login
import config
from views import LoginScreen, AdminDashboard, ManagerDashboard, FrontDeskDashboard, MaintenanceDashboard, FinanceManagerDashboard, TenantDashboard

# Setup route map for different user roles and their respective dashboard frames
ROLE_FRAME_MAP = {
    'ADMINISTRATOR': AdminDashboard,
    'MANAGER': ManagerDashboard,
    'FRONT_DESK': FrontDeskDashboard,
    'MAINTENANCE': MaintenanceDashboard,
    'FINANCE_MANAGER': FinanceManagerDashboard,
    'TENANT': TenantDashboard,
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
            
        # Determine the user's role
        user_role = user.role
        
        # If user has no staff role but has a tenant_id, they are a tenant
        if not user_role and getattr(user, 'tenant_id', None):
            user_role = 'TENANT'
        
        # Look up the correct frame class. Default to AdminDashboard for now 
        # so you don't crash while testing if the role is missing.
        FrameClass = ROLE_FRAME_MAP.get(user_role, AdminDashboard)
        
        # Instantiate the correct dashboard and pack it
        self.current_frame = FrameClass(parent=self, user=user)
        self.current_frame.pack(fill="both", expand=True)

    def logout(self):
        """ Logs the user out and returns to the login screen. """
        self.show_login_screen()


def initialise() -> None:
    app = App()
    app.mainloop()