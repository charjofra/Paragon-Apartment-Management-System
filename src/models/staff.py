from .user import User

class Staff(User):
    def __init__(self, user_id: int, location_id: int, full_name: str, email: str, password_hash: str, created_at: float, is_active: bool, role: str) -> None:
        super().__init__(user_id, location_id, full_name, email, password_hash, created_at, is_active)
        self.role = role