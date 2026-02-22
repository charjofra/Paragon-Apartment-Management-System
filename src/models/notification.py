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