from .staff import Staff
from .maintenance_request import MaintenanceRequest

class MaintenanceResolution:
    def __init__(self, resolution_id: int, maintenance_request: MaintenanceRequest, date_resolved: float, description: str, time_taken: float, cost: float, recorded_by: Staff) -> None:
        self.resolution_id = resolution_id
        self.maintenance_request = maintenance_request
        self.date_resolved = date_resolved
        self.description = description
        self.time_taken = time_taken
        self.cost = cost
        self.recorded_by = recorded_by