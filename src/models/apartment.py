from .location import Location

class Apartment:
    def __init__(self, apartment_id: int, apt_location: Location, unit_code: str, apt_type: str, monthly_rent: float, rooms: int, status: str, created_at: float) -> None:
        self.apartment_id = apartment_id
        self.location = apt_location
        self.unit_code = unit_code
        self.apt_type = apt_type
        self.monthly_rent = monthly_rent
        self.rooms = rooms
        self.status = status
        self.created_at = created_at
    
    def get_apartment_id(self) -> int:
        return self.apartment_id
    
    def get_location(self) -> Location:
        return self.location

    def get_unit_code(self) -> str:
        return self.unit_code
    
    def get_apt_type(self) -> str:
        return self.apt_type
    
    def get_monthly_rent(self) -> float:
        return self.monthly_rent
    
    def get_rooms(self) -> int:
        return self.rooms   
    
    def get_status(self) -> str:
        return self.status
    
    def get_created_at(self) -> float:
        return self.created_at
    
    def set_apartment_id(self, apartment_id: int) -> None:
        self.apartment_id = apartment_id
        
    def set_location(self, apt_location: Location) -> None:
        self.location = apt_location
        
    def set_unit_code(self, unit_code: str) -> None:
        self.unit_code = unit_code
    
    def set_apt_type(self, apt_type: str) -> None:
        self.apt_type = apt_type
        
    def set_monthly_rent(self, monthly_rent: float) -> None:
        self.monthly_rent = monthly_rent
        
    def set_rooms(self, rooms: int) -> None:
        self.rooms = rooms
        
    def set_status(self, status: str) -> None:
        self.status = status
        
    def set_created_at(self, created_at: float) -> None:
        self.created_at = created_at