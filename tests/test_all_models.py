import pytest
import time
from models.user import User
from models.tenant import Tenant
from models.apartment import Apartment
from models.staff import Staff
from models.lease import Lease
from models.invoice import Invoice
from models.payment import Payment
from models.maintenance_request import MaintenanceRequest

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
    """Test that a Tenant object is created successfully."""
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
    assert apt.monthly_rent == 1200.00

def test_staff_creation_success():
    """Test that a Staff object (inheriting from User) is created properly."""
    test_time = time.time()
    staff = Staff(
        user_id=3,
        location_id=101,
        full_name="Alice Admin",
        email="alice@test.com",
        password_hash="adminpass",
        is_staff=True,
        date_created=test_time,
        is_active=True,
        role="Admin"
    )
    
    assert staff.user_id == 3
    assert staff.role == "Admin"
    assert staff.is_staff is True

def test_lease_creation_success():
    """Test creating a Lease, which requires Tenant and Apartment objects."""
    test_time = time.time()
    tenant = Tenant(2, 101, "Jane Smith", "jane@example.com", "pass", False, test_time, True, 50, "NI", "Job", "Ref", "Req")
    apt = Apartment(1, 101, "B202", "2-Bedroom", 1200.00, 2, "Occupied", test_time)
    
    lease = Lease(
        lease_id=10,
        tenant=tenant,
        apartment=apt,
        start_date=test_time,
        end_date=test_time + 31536000,
        monthly_rent=1200.00,
        status="Active"
    )
    
    assert lease.lease_id == 10
    assert lease.tenant.full_name == "Jane Smith"
    assert lease.apartment.unit_code == "B202"
    assert lease.status == "Active"

def test_invoice_and_payment_creation():
    """Test creating an Invoice and a Payment linking multiple objects."""
    test_time = time.time()
    staff = Staff(3, 101, "Manager", "mgr@test.com", "pass", True, test_time, True, "Manager")
    tenant = Tenant(2, 101, "Jane Smith", "jane@example.com", "pass", False, test_time, True, 50, "NI", "Job", "Ref", "Req")
    apt = Apartment(1, 101, "B202", "2-Bedroom", 1200.00, 2, "Occupied", test_time)
    lease = Lease(10, tenant, apt, test_time, test_time + 31536000, 1200.00, "Active")
    
    invoice = Invoice(
        invoice_id=100,
        tenant=tenant,
        lease=lease,
        date_issued=test_time,
        date_due=test_time + 864000,
        amount=1200.00,
        status="Pending",
        last_notified=test_time
    )
    
    payment = Payment(
        payment_id=500,
        invoice=invoice,
        date_paid=test_time + 1000,
        amount_paid=1200.00,
        payment_method="Card",
        recorded_by=staff
    )
    
    assert invoice.amount == 1200.00
    assert invoice.status == "Pending"
    assert payment.payment_id == 500
    assert payment.amount_paid == 1200.00
    assert payment.recorded_by.role == "Manager"

def test_maintenance_request_creation():
    """Test creating a maintenance request with staff and tenant roles."""
    test_time = time.time()
    m_staff = Staff(4, 101, "Maintenance Guy", "m@test.com", "pass", True, test_time, True, "Maintenance Staff")
    f_staff = Staff(5, 101, "Front Desk", "f@test.com", "pass", True, test_time, True, "Front Desk")
    tenant = Tenant(2, 101, "Jane Smith", "jane.smith@example.com", "pass", False, test_time, True, 50, "NI", "Job", "Ref", "Req")
    apt = Apartment(1, 101, "B202", "2-Bedroom", 1200.00, 2, "Occupied", test_time)
    lease = Lease(10, tenant, apt, test_time, test_time + 86400, 1200.00, "Active")

    req = MaintenanceRequest(
        request_id=202,
        tenant=tenant,
        apartment=apt,
        lease=lease,
        date_created=test_time,
        description="Leaky faucet",
        priority="High",
        status="Assigned",
        scheduled_for=test_time + 86400,
        assigned_to=m_staff,
        assigned_by=f_staff
    )

    assert req.description == "Leaky faucet"
    assert req.assigned_to.role == "Maintenance Staff"
    assert req.tenant.full_name == "Jane Smith"
