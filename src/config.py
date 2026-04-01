import os
from dotenv import load_dotenv

# Database settings
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456789"),
    "database": os.getenv("DB_NAME", "paragon_apartment_management_system"),
}

# Application settings
APP_TITLE: str = "Property Management System"
APPEARANCE_MODE: str = "System"
COLOR_THEME: str = "assets/themes/paragon.json"
DEBUG_MODE: bool = True # SET TO FALSE WHEN WE R DONE

# Window settings
WINDOW_SCALE: float = 0.75
