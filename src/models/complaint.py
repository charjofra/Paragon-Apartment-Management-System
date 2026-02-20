from tenant import Tenant
from staff import Staff
from lease import Lease

class Complaint:
    def __init__(self, complaint_id: int, tenant: Tenant, lease: Lease, date_created: float, description: str, status: str, handled_by: Staff) -> None:
        self.complaint_id = complaint_id
        self.tenant = tenant
        self.lease = lease
        self.date_created = date_created
        self.description = description
        self.status = status
        self.handled_by = handled_by
    
    def get_complaint_id(self) -> int:
        return self.complaint_id
    
    def get_tenant(self) -> Tenant:
        return self.tenant
    
    def get_lease(self) -> Lease:
        return self.lease
    
    def get_date_created(self) -> float:
        return self.date_created
    
    def get_description(self) -> str:
        return self.description
    
    def get_status(self) -> str:
        return self.status
    
    def get_handled_by(self) -> Staff:
        return self.handled_by
    
    def set_complaint_id(self, complaint_id: int) -> None:
        self.complaint_id = complaint_id
        
    def set_tenant(self, tenant: Tenant) -> None:
        self.tenant = tenant
        
    def set_lease(self, lease: Lease) -> None:
        self.lease = lease
        
    def set_date_created(self, date_created: float) -> None:
        self.date_created = date_created
        
    def set_description(self, description: str) -> None:
        self.description = description
        
    def set_status(self, status: str) -> None:
        self.status = status
        
    def set_handled_by(self, handled_by: Staff) -> None:
        self.handled_by = handled_by