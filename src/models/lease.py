from .tenant import Tenant
from .apartment import Apartment

class Lease:
    def __init__(self, lease_id: int, tenant: Tenant, apartment: Apartment, start_date: float, end_date: float, monthly_rent: float, status: str) -> None:
        self.lease_id = lease_id
        self.tenant = tenant
        self.apartment = apartment
        self.start_date = start_date
        self.end_date = end_date
        self.monthly_rent = monthly_rent
        self.status = status
    
    def get_lease_id(self) -> int:
        return self.lease_id

    def get_tenant(self) -> Tenant:
        return self.tenant
    
    def get_apartment(self) -> Apartment:
        return self.apartment
    
    def get_start_date(self) -> float:
        return self.start_date
    
    def get_end_date(self) -> float:
        return self.end_date
    
    def get_monthly_rent(self) -> float:
        return self.monthly_rent
    
    def get_status(self) -> str:
        return self.status
    
    def set_lease_id(self, lease_id: int) -> None:
        self.lease_id = lease_id
        
    def set_tenant(self, tenant: Tenant) -> None:
        self.tenant = tenant
        
    def set_apartment(self, apartment: Apartment) -> None:
        self.apartment = apartment
        
    def set_start_date(self, start_date: float) -> None:
        self.start_date = start_date
        
    def set_end_date(self, end_date: float) -> None:
        self.end_date = end_date
        
    def set_monthly_rent(self, monthly_rent: float) -> None:
        self.monthly_rent = monthly_rent
        
    def set_status(self, status: str) -> None:
        self.status = status