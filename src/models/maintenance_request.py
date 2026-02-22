from .tenant import Tenant
from .staff import Staff
from .apartment import Apartment
from .lease import Lease

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