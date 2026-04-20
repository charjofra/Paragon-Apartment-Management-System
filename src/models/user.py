class User:
    def __init__(self, user_id: int, location_id: int, full_name: str, email: str, password_hash: str, is_staff: bool, date_created: float, is_active: bool, staff_id: int = None, role: str = None, tenant_id: int = None) -> None:
        if "@" not in email:
            raise ValueError("Invalid email format.")
        if not full_name or len(full_name.strip()) == 0:
            raise ValueError("Full name cannot be empty.")
            
        self.user_id = user_id
        self.location_id = location_id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.is_staff = is_staff
        self.date_created = date_created
        self.is_active = is_active
        self.staff_id = staff_id
        self.role = role
        self.tenant_id = tenant_id