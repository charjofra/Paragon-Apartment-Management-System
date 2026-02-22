class Location:
    def __init__(self, location_id: int, city: str, address: str, created_at: float) -> None:
        self.location_id = location_id
        self.city = city
        self.address = address
        self.created_at = created_at