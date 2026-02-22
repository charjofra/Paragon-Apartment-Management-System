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