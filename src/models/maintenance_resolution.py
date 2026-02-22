from staff import Staff
from maintenance_request import MaintenanceRequest

class MaintenanceResolution:
    def __init__(self, resolution_id: int, maintenance_request: MaintenanceRequest, date_resolved: float, description: str, time_taken: float, cost: float, recorded_by: Staff) -> None:
        self.resolution_id = resolution_id
        self.maintenance_request = maintenance_request
        self.date_resolved = date_resolved
        self.description = description
        self.time_taken = time_taken
        self.cost = cost
        self.recorded_by = recorded_by
    
    def get_resolution_id(self) -> int:
        return self.resolution_id
    
    def get_maintenance_request(self) -> MaintenanceRequest:
        return self.maintenance_request
    
    def get_date_resolved(self) -> float:
        return self.date_resolved
    
    def get_description(self) -> str:
        return self.description
    
    def get_time_taken(self) -> float:
        return self.time_taken
    
    def get_cost(self) -> float:
        return self.cost
    
    def get_recorded_by(self) -> Staff:
        return self.recorded_by
    
    def set_resolution_id(self, resolution_id: int) -> None:
        self.resolution_id = resolution_id
        
    def set_maintenance_request(self, maintenance_request: MaintenanceRequest) -> None:
        self.maintenance_request = maintenance_request
        
    def set_date_resolved(self, date_resolved: float) -> None:
        self.date_resolved = date_resolved
    
    def set_description(self, description: str) -> None:
        self.description = description
    
    def set_time_taken(self, time_taken: float) -> None:
        self.time_taken = time_taken
        
    def set_cost(self, cost: float) -> None:
        self.cost = cost
        
    def set_recorded_by(self, recorded_by: Staff) -> None:
        self.recorded_by = recorded_by