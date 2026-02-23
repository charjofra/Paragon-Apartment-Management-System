class User:
    def __init__(self, user_id: int, location_id: int, full_name: str, email: str, password_hash: str, is_staff: bool, created_at: float, is_active: bool) -> None:
        self.user_id = user_id
        self.location_id = location_id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.is_staff = is_staff
        self.created_at = created_at
        self.is_active = is_active