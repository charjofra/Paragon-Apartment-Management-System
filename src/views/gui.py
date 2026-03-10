import customtkinter as ctk
from services.user_service import login
import config
from views import LoginScreen, AdminDashboard, ManagerDashboard, FrontDeskDashboard, MaintenanceDashboard, FinanceManagerDashboard, TenantDashboard

ROLE_FRAME_MAP = {
    'ADMINISTRATOR': AdminDashboard,
    'MANAGER': ManagerDashboard,
    'FRONT_DESK': FrontDeskDashboard,
    'MAINTENANCE_STAFF': MaintenanceDashboard,
    'FINANCE_MANAGER': FinanceManagerDashboard,
    'TENANT': TenantDashboard,
}

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        self.screen_width: int = self.winfo_screenwidth()
        self.screen_height: int = self.winfo_screenheight()
        
        self.geometry(f"{int(self.screen_width*config.WINDOW_SCALE)}x{int(self.screen_height*config.WINDOW_SCALE)}")
        self.after(1, self.wm_state, "zoomed")
        self.title(config.APP_TITLE)
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        self.current_frame = None
        
        self.show_login_screen()
        
    def show_login_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = LoginScreen(
            parent=self, 
            screen_width=self.screen_width, 
            screen_height=self.screen_height, 
            on_login_attempt=self.handle_login 
        )
        self.current_frame.pack(fill="both", expand=True)

    def handle_login(self, email: str, password: str) -> None:
        """ Processes the login attempt passed up from the LoginScreen. """
        
        user = login(email, password)
        
        if user is None:
            self.current_frame.show_error("Invalid email or password.")
        else:
            print(f"Successfully logged in as {user.full_name}!")
            
            self.show_dashboard(user)

    def show_dashboard(self, user) -> None:
        """
        The scalable router. Destroys the login screen and loads the 
        correct dashboard based on the user's role.
        """
        
        if self.current_frame:
            self.current_frame.destroy()
            
        user_role = user.role
        
        if not user_role and getattr(user, 'tenant_id', None):
            user_role = 'TENANT'
        
        # default to admin only while testing, remember to change this!!!!
        FrameClass = ROLE_FRAME_MAP.get(user_role, AdminDashboard)
        
        self.current_frame = FrameClass(parent=self, user=user)
        self.current_frame.pack(fill="both", expand=True)

    def logout(self):
        """ Logs the user out and returns to the login screen. """
        self.show_login_screen()


def initialise() -> None:
    app = App()
    app.mainloop()