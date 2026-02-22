from .tenant import Tenant
from .lease import Lease

class Invoice:
    def __init__(self, invoice_id: int, tenant: Tenant, lease: Lease, date_issued: float, date_due: float, amount: float, status: str, last_notified: float) -> None:
        self.invoice_id = invoice_id
        self.tenant = tenant
        self.lease = lease
        self.date_issued = date_issued
        self.date_due = date_due
        self.amount = amount
        self.status = status
        self.last_notified = last_notified