from .tenant import Tenant
from .staff import Staff
from .lease import Lease

class Complaint:
    def __init__(self, complaint_id: int, tenant: Tenant, lease: Lease, date_created: float, description: str, status: str, handled_by: Staff) -> None:
        self.complaint_id = complaint_id
        self.tenant = tenant
        self.lease = lease
        self.date_created = date_created
        self.description = description
        self.status = status
        self.handled_by = handled_by