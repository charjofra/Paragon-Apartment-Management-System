from .user import User

class Tenant(User):
    def __init__(self, user_id: int, location_id: int, full_name: str, email: str, password_hash: str, created_at: float, is_active: bool, tenant_id: int, ni_number: str, occupation: str, references_txt: str, requirements: str) -> None:
        super().__init__(user_id, location_id, full_name, email, password_hash, created_at, is_active)
        self.tenant_id = tenant_id
        self.ni_number = ni_number
        self.occupation = occupation
        self.references_txt = references_txt
        self.requirements = requirements