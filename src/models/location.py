class Location:
    def __init__(self, location_id: int, city: str, address: str, created_at: float) -> None:
        self.location_id = location_id
        self.city = city
        self.address = address
        self.created_at = created_at
    
    def get_location_id(self) -> int:
        return self.location_id
    
    def get_city(self) -> str:
        return self.city
    
    def get_address(self) -> str:
        return self.address
    
    def get_created_at(self) -> float:
        return self.created_at
    
    def set_location_id(self, location_id: int) -> None:
        self.location_id = location_id
        
    def set_city(self, city: str) -> None:
        self.city = city
        
    def set_address(self, address: str) -> None: 
        self.address = address
        
    def set_created_at(self, created_at: float) -> None:
        self.created_at = created_at