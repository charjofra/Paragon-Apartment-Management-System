from .user import User

class Staff(User):
    def __init__(self, user_id: int, location_id: int, full_name: str, email: str, password_hash: str, is_staff: bool, date_created: float, is_active: bool, role: str) -> None:
        super().__init__(user_id, location_id, full_name, email, password_hash, is_staff, date_created, is_active)
        self.role = role