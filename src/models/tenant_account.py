from datetime import datetime

class TenantAccount:
    def __init__(self, tenant_account_id: int, tenant_id: int, email: str, password_hash: str, is_active: bool = True, created_at: datetime | None = None,) -> None:
        self.tenant_account_id = tenant_account_id
        self.tenant_id = tenant_id
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = created_at