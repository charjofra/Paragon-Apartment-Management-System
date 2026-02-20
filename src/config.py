import os
from dotenv import load_dotenv
import mysql.connector

# Database settings
<<<<<<< HEAD
DB_HOST: str = "localhost"
DB_PORT: int = 3306
DB_USER: str = "root"
DB_PASSWORD: str = "PaSsWoRd!6480?"
DB_NAME: str = "paragon_apartment_management_system"
=======
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "paragon_apartment_management_system"),
}

def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
>>>>>>> 5f87a4d2ba5a8654c431e13a966d91c013c88ece

# Application settings
APP_TITLE: str = "Property Management System"
APPEARANCE_MODE: str = "dark"
COLOR_THEME: str = "dark-blue"
LOGIN_BG_IMAGE: str = "images/temp_login_background.jpg"

# Window settings
WINDOW_SCALE: float = 0.75
