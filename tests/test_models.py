import pytest
import time
from models.user import User
from models.tenant import Tenant
from models.apartment import Apartment

def test_user_creation_success():
    """Test that a User object is created successfully with valid data."""
    test_time = time.time()
    user = User(
        user_id=1,
        location_id=101,
        full_name="John Doe",
        email="john@test.com",
        password_hash="pass123",
        is_staff=False,
        date_created=test_time,
        is_active=True
    )
    
    assert user.user_id == 1
    assert user.full_name == "John Doe"
    assert user.email == "john@test.com"
    assert user.is_staff is False
    assert user.is_active is True

def test_tenant_creation_success():
    """Test that a Tenant object (inheriting from User) is created successfully."""
    test_time = time.time()
    tenant = Tenant(
        user_id=2, 
        location_id=101, 
        full_name="Jane Smith", 
        email="jane.smith@example.com", 
        password_hash="securepass", 
        is_staff=False, 
        date_created=test_time, 
        is_active=True, 
        tenant_id=50, 
        ni_number="AB123456C", 
        occupation="Data Analyst", 
        references_txt="Excellent tenant", 
        requirements="Needs parking"
    )
    
    assert tenant.tenant_id == 50
    assert tenant.full_name == "Jane Smith"
    assert tenant.ni_number == "AB123456C"
    assert tenant.occupation == "Data Analyst"
    # Testing inherited attribute
    assert tenant.email == "jane.smith@example.com"

def test_apartment_creation_success():
    """Test that an Apartment object is created successfully."""
    test_time = time.time()
    apt = Apartment(
        apartment_id=1,
        location_id=101,
        unit_code="B202",
        apt_type="2-Bedroom",
        monthly_rent=1200.00,
        rooms=2,
        status="Occupied",
        date_created=test_time
    )
    
    assert apt.apartment_id == 1
    assert apt.unit_code == "B202"
    assert apt.apt_type == "2-Bedroom"
    assert apt.monthly_rent == 1200.00
    assert apt.rooms == 2
    assert apt.status == "Occupied"
