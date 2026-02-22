from .user import User
from .location import Location

class Staff(User):
    def __init__(self, user_id: int, user_location: Location, full_name: str, email: str, password_hash: str, created_at: float, is_active: bool, role: str) -> None:
        super().__init__(user_id, user_location, full_name, email, password_hash, created_at, is_active)
        self.role = role