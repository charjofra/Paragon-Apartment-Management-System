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
    
    def get_invoice_id(self) -> int:
        return self.invoice_id
    
    def get_tenant(self) -> Tenant:
        return self.tenant
    
    def get_lease(self) -> Lease:
        return self.lease
    
    def get_date_issued(self) -> float:
        return self.date_issued
    
    def get_date_due(self) -> float:
        return self.date_due
    
    def get_amount(self) -> float:
        return self.amount
    
    def get_status(self) -> str:
        return self.status
    
    def get_last_notified(self) -> float:
        return self.last_notified
    
    def set_invoice_id(self, invoice_id: int) -> None:
        self.invoice_id = invoice_id
        
    def set_tenant(self, tenant: Tenant) -> None:
        self.tenant = tenant
        
    def set_lease(self, lease: Lease) -> None:
        self.lease = lease
        
    def set_date_issued(self, date_issued: float) -> None:
        self.date_issued = date_issued
        
    def set_date_due(self, date_due: float) -> None:
        self.date_due = date_due
        
    def set_amount(self, amount: float) -> None:
        self.amount = amount
    
    def set_status(self, status: str) -> None:
        self.status = status
        
    def set_last_notified(self, last_notified: float) -> None:
        self.last_notified = last_notified