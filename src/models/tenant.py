from .user import User
from .location import Location

class Tenant(User):
    def __init__(self, user_id: int, user_location: Location, full_name: str, email: str, password_hash: str, created_at: float, is_active: bool, tenant_id: int, ni_number: str, occupation: str, references_txt: str, requirements: str) -> None:
        super().__init__(user_id, user_location, full_name, email, password_hash, created_at, is_active)
        self.tenant_id = tenant_id
        self.ni_number = ni_number
        self.occupation = occupation
        self.references_txt = references_txt
        self.requirements = requirements
    
    def get_tenant_id(self) -> int:
        return self.tenant_id

    def get_ni_number(self) -> str:
        return self.ni_number

    def get_occupation(self) -> str:
        return self.occupation

    def get_references_txt(self) -> str:
        return self.references_txt

    def get_requirements(self) -> str:
        return self.requirements

    def set_tenant_id(self, tenant_id: int) -> None:
        self.tenant_id = tenant_id
    
    def set_ni_number(self, ni_number: str) -> None:
        self.ni_number = ni_number
    
    def set_occupation(self, occupation: str) -> None:
        self.occupation = occupation
    
    def set_references_txt(self, references_txt: str) -> None:
        self.references_txt = references_txt
    
    def set_requirements(self, requirements: str) -> None:
        self.requirements = requirements