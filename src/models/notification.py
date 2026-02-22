from .tenant import Tenant
from .staff import Staff

class Notification:
    def __init__(self, notification_id: int, tenant: Tenant, staff: Staff, type: str, message: str, date_sent: float) -> None:
        self.notification_id = notification_id
        self.tenant = tenant
        self.staff = staff
        self.type = type
        self.message = message
        self.date_sent = date_sent
    
    def get_notification_id(self) -> int:
        return self.notification_id
    
    def get_tenant(self) -> Tenant:
        return self.tenant
    
    def get_staff(self) -> Staff:
        return self.staff
    
    def get_type(self) -> str:
        return self.type
    
    def get_message(self) -> str:
        return self.message
    
    def get_date_sent(self) -> float:
        return self.date_sent
    
    def set_notification_id(self, notification_id: int) -> None:
        self.notification_id = notification_id
        
    def set_tenant(self, tenant: Tenant) -> None:
        self.tenant = tenant
        
    def set_staff(self, staff: Staff) -> None:
        self.staff = staff
        
    def set_type(self, type: str) -> None:
        self.type = type
        
    def set_message(self, message: str) -> None:
        self.message = message
        
    def set_date_sent(self, date_sent: float) -> None:
        self.date_sent = date_sent