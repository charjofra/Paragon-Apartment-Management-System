from tenant import Tenant
from staff import Staff
from apartment import Apartment
from lease import Lease

class MaintenanceRequest:
    def __init__(self, request_id: int, tenant: Tenant, apartment: Apartment, lease: Lease, date_created: float, description: str, priority: str, status: str, scheduled_for: float, assigned_to: Staff, assigned_by: Staff) -> None:
        self.request_id = request_id
        self.tenant = tenant
        self.apartment = apartment
        self.lease = lease
        self.date_created = date_created
        self.description = description
        self.priority = priority
        self.status = status
        self.scheduled_for = scheduled_for
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
    
    def get_request_id(self) -> int:
        return self.request_id
    
    def get_tenant(self) -> Tenant:
        return self.tenant
    
    def get_apartment(self) -> Apartment:
        return self.apartment
    
    def get_lease(self) -> Lease:
        return self.lease
    
    def get_date_created(self) -> float:
        return self.date_created
    
    def get_description(self) -> str:
        return self.description
    
    def get_priority(self) -> str:
        return self.priority
    
    def get_status(self) -> str:
        return self.status
    
    def get_scheduled_for(self) -> float:
        return self.scheduled_for
    
    def get_assigned_to(self) -> Staff:
        return self.assigned_to
    
    def get_assigned_by(self) -> Staff:
        return self.assigned_by
    
    def set_request_id(self, request_id: int) -> None:
        self.request_id = request_id
        
    def set_tenant(self, tenant: Tenant) -> None:
        self.tenant = tenant
        
    def set_apartment(self, apartment: Apartment) -> None:
        self.apartment = apartment
        
    def set_lease(self, lease: Lease) -> None:
        self.lease = lease
        
    def set_date_created(self, date_created: float) -> None:
        self.date_created = date_created
        
    def set_description(self, description: str) -> None:
        self.description = description
        
    def set_priority(self, priority: str) -> None:
        self.priority = priority
        
    def set_status(self, status: str) -> None:
        self.status = status
        
    def set_scheduled_for(self, scheduled_for: float) -> None:
        self.scheduled_for = scheduled_for
        
    def set_assigned_to(self, assigned_to: Staff) -> None:
        self.assigned_to = assigned_to
        
    def set_assigned_by(self, assigned_by: Staff) -> None:
        self.assigned_by = assigned_by