import bcrypt
from .models import User
from .execute_sql import execute_read, execute_write

def login(email: str, password: str):
    # Staff login using email + password.
    # Returns a dict with user data if valid, otherwise None.
    
    query = """
        SELECT user_id, location_id, full_name, email, password_hash, role, is_active
        FROM users
        WHERE email = %s
    """
    
    results = execute_read(query, (email,))

    # execute_read returns a list. If it's empty, the user wasn't found.
    if not results:
        return None

    # Grab the first (and should be only) user record
    user = results[0]

    # Check if the account is active
    if user["is_active"] != 1:
        return None

    stored_hash = user["password_hash"]

    # bcrypt expects bytes
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return None

    # don't return the hash to the rest of the app
    user.pop("password_hash", None)
    return user

def create_user(full_name: str, email: str, password: str, role: str, location_id=None):
    # Creates a new user in the database.
    #Returns the new user's ID.
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    query = """
        INSERT INTO users (location_id, full_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    return execute_write(query, (location_id, full_name, email, password_hash, role))
