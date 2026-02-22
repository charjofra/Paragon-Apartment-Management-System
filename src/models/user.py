from .location import Location

class User:
    def __init__(self, user_id: int, user_location: Location, full_name: str, email: str, password_hash: str, created_at: float, is_active: bool) -> None:
        self.user_id = user_id
        self.location = user_location
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.is_active = is_active