import bcrypt
from config import get_db_connection

def login(email: str, password: str):
    """
    Staff login using email + password.
    Returns a dict with user data if valid, otherwise None.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT user_id, location_id, full_name, email, password_hash, role, is_active
            FROM users
            WHERE email = %s
            """,
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return None

        if user["is_active"] != 1:
            return None

        stored_hash = user["password_hash"]

        # bcrypt expects bytes
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return None

        # don't return the hash to the rest of the app
        user.pop("password_hash", None)
        return user

    finally:
        conn.close()

def create_user(full_name: str, email: str, password: str, role: str, location_id=None):
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    if conn is None:
        raise Exception("Failed to connect to database. Check your .env credentials.")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (location_id, full_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (location_id, full_name, email, password_hash, role)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
