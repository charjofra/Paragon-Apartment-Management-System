import os
from dotenv import load_dotenv

# Database settings
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "paragon_apartment_management_system"),
}

# Application settings
APP_TITLE: str = "Property Management System"
APPEARANCE_MODE: str = "dark"
COLOR_THEME: str = "dark-blue"
LOGIN_BG_IMAGE: str = "images/temp_login_background.jpg"

# Window settings
WINDOW_SCALE: float = 0.75
