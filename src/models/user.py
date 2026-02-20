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

    def get_user_id(self) -> int:
        return self.user_id
    
    def get_location(self) -> Location:
        return self.location

    def get_full_name(self) -> str:
        return self.full_name

    def get_email(self) -> str:
        return self.email
    
    def get_password_hash(self) -> str:
        return self.password_hash
    
    def get_is_active(self) -> bool:
        return self.is_active
    
    def get_created_at(self) -> float:
        return self.created_at
    
    def set_user_id(self, user_id: int) -> None:
        self.user_id = user_id
        
    def set_location(self, user_location: Location) -> None:
        self.location = user_location
        
    def set_full_name(self, full_name: str) -> None:
        self.full_name = full_name
    
    def set_email(self, email: str) -> None:
        self.email = email
    
    def set_password_hash(self, password_hash: str) -> None:
        self.password_hash = password_hash
        
    def set_is_active(self, is_active: bool) -> None:
        self.is_active = is_active
        
    def set_created_at(self, created_at: float) -> None:
        self.created_at = created_at