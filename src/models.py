class Location:
    def __init__(self, location_id, city, address, created_at) -> None:
        self.location_id = location_id
        self.city = city
        self.address = address
        self.created_at = created_at
    
    def get_location_id(self) -> int:
        return self.location_id
    
    def get_city(self) -> str:
        return self.city
    
    def get_address(self) -> str:
        return self.address
    
    def get_created_at(self) -> float:
        return self.created_at
    
    def set_location_id(self, location_id) -> None:
        self.location_id = location_id
        
    def set_city(self, city) -> None:
        self.city = city
        
    def set_address(self, address) -> None: 
        self.address = address
        
    def set_created_at(self, created_at) -> None:
        self.created_at = created_at
        

class User (Location):
    def __init__(self, user_id, location_id, city, address, full_name, email, password_hash, created_at, is_active, role) -> None:
        super().__init__(location_id, city, address, created_at)
        self.user_id = user_id
        self.location_id = location_id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.role = role

    def get_user_id(self) -> int:
        return self.user_id

    def get_full_name(self) -> str:
        return self.full_name

    def get_email(self) -> str:
        return self.email
    
    def get_password_hash(self) -> str:
        return self.password_hash
    
    def get_role(self) -> str:
        return self.role
    
    def get_is_active(self) -> bool:
        return self.is_active
    
    def set_user_id(self, user_id) -> None:
        self.user_id = user_id
        
    def set_full_name(self, full_name) -> None:
        self.full_name = full_name
    
    def set_email(self, email) -> None:
        self.email = email
    
    def set_password_hash(self, password_hash) -> None:
        self.password_hash = password_hash
    
    def set_role(self, role) -> None:
        self.role = role
        
    def set_is_active(self, is_active) -> None:
        self.is_active = is_active
    
        
class Apartment(Location):
    def __init__(self, location_id, city, address, apartment_id, unit_code, apt_type, monthly_rent, rooms, status, created_at) -> None:
        super().__init__(location_id, city, address, created_at)
        self.apartment_id = apartment_id
        self.unit_code = unit_code
        self.apt_type = apt_type
        self.monthly_rent = monthly_rent
        self.rooms = rooms
        self.status = status
    
    def get_apartment_id(self) -> int:
        return self.apartment_id

    def get_unit_code(self) -> str:
        return self.unit_code
    
    def get_apt_type(self) -> str:
        return self.apt_type
    
    def get_monthly_rent(self) -> float:
        return self.monthly_rent
    
    def get_rooms(self) -> int:
        return self.rooms   
    
    def get_status(self) -> str:
        return self.status
    
    def set_apartment_id(self, apartment_id) -> None:
        self.apartment_id = apartment_id
        
    def set_unit_code(self, unit_code) -> None:
        self.unit_code = unit_code
    
    def set_apt_type(self, apt_type) -> None:
        self.apt_type = apt_type
        
    def set_monthly_rent(self, monthly_rent) -> None:
        self.monthly_rent = monthly_rent
        
    def set_rooms(self, rooms) -> None:
        self.rooms = rooms
        
    def set_status(self, status) -> None:
        self.status = status
        
class Tenant(User):
    def __init__(self, user_id, location_id, city, address, full_name, email, password_hash, created_at, is_active, role, tenant_id, ni_number, occupation, references_txt, requirements) -> None:
        super().__init__(user_id, location_id, city, address, full_name, email, password_hash, created_at, is_active, role)
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

    def set_tenant_id(self, tenant_id) -> None:
        self.tenant_id = tenant_id
    
    def set_ni_number(self, ni_number) -> None:
        self.ni_number = ni_number
    
    def set_occupation(self, occupation) -> None:
        self.occupation = occupation
    
    def set_references_txt(self, references_txt) -> None:
        self.references_txt = references_txt
    
    def set_requirements(self, requirements) -> None:
        self.requirements = requirements
