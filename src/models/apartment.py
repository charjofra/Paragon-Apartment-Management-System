class Apartment:
    def __init__(self, apartment_id: int, location_id: int, unit_code: str, apt_type: str, monthly_rent: float, rooms: int, status: str, date_created: float) -> None:
        if monthly_rent < 0:
            raise ValueError("Rent cannot be negative.")
        if rooms < 0:
            raise ValueError("Rooms cannot be negative.")
        if not unit_code or len(unit_code.strip()) == 0:
            raise ValueError("Unit code cannot be empty.")
            
        self.apartment_id = apartment_id
        self.location_id = location_id
        self.unit_code = unit_code
        self.apt_type = apt_type
        self.monthly_rent = monthly_rent
        self.rooms = rooms
        self.status = status
        self.date_created = date_created