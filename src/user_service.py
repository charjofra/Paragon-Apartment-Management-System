import bcrypt
import time
from models import User
from db_utils import execute_read, execute_write

def login(email: str, password: str) -> User | None:
    """
    login using email only (password temporarily disabled).
    Returns a User object if email exists and account is active, otherwise None.
    """

    query = """
        SELECT u.user_id, u.location_id, u.full_name, u.email, u.password_hash,
               u.is_staff, u.is_active, u.date_created,
               s.staff_id, s.role,
               t.tenant_id
        FROM users u
        LEFT JOIN staff s ON u.user_id = s.user_id
        LEFT JOIN tenants t ON u.user_id = t.user_id
        WHERE u.email = %s
    """

    results = execute_read(query, (email,))

    # If no user found
    if not results:
        return None

    user_data = results[0]

    # Check if the account is active
    if user_data["is_active"] != 1:
        return None

    # -------- PASSWORD CHECK DISABLED --------
    # stored_hash = user_data["password_hash"]
    # if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
    #     return None
    # ------------------------------------------

    return User(
        user_id=user_data["user_id"],
        location_id=user_data["location_id"],
        full_name=user_data["full_name"],
        email=user_data["email"],
        password_hash="",
        is_staff=user_data["is_staff"],
        date_created=user_data["date_created"],
        is_active=bool(user_data["is_active"]),
        staff_id=user_data["staff_id"],
        role=user_data["role"],
        tenant_id=user_data["tenant_id"]
    )

def create_user(full_name: str, email: str, password: str, is_staff: bool, location_id: int = None) -> User:
    """
    Creates a new user in the database.
    Returns the new user as a User object.
    """
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    query = """
        INSERT INTO users (location_id, full_name, email, password_hash, is_staff)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    new_user_id = execute_write(query, (location_id, full_name, email, password_hash, is_staff))
    
    return User(
        user_id=new_user_id,
        location_id=location_id,
        full_name=full_name,
        email=email,
        password_hash=password_hash,
        is_staff=is_staff,
        date_created=time.time(),
        is_active=True
    )