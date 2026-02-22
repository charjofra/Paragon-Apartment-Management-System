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