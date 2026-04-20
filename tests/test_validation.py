import pytest
from models.apartment import Apartment
from models.user import User

def test_apartment_negative_rent_fails():
    """
    Test that invalid data (negative rent) throws a ValueError.
    Note: To pass this test, you MUST add a check like IF monthly_rent < 0 RAISE ValueError in apartment.py
    """
    with pytest.raises(ValueError):
        # We are intentionally injecting BAD DATA
        apt = Apartment(
            apartment_id=1,
            location_id=101,
            unit_code="A100",
            apt_type="Studio",
            monthly_rent=-500.00,  # Invalid: Rent below 0
            rooms=1,
            status="Available",
            date_created=100.0
        )

def test_user_invalid_email_fails():
    """
    Test that invalid data (no @ in email) throws a ValueError.
    Note: To pass this test, you MUST add a check like IF '@' not in email RAISE ValueError in user.py
    """
    with pytest.raises(ValueError):
        user = User(
            user_id=1,
            location_id=101,
            full_name="John Doe",
            email="NotAnEmail",  # Invalid: No @ symbol
            password_hash="pass123",
            is_staff=False,
            date_created=100.0,
            is_active=True
        )

def test_apartment_negative_rooms_fails():
    """
    Test that an apartment cannot be created with negative rooms.
    """
    with pytest.raises(ValueError):
        apt = Apartment(
            apartment_id=2,
            location_id=101,
            unit_code="A101",
            apt_type="Studio",
            monthly_rent=500.00,
            rooms=-1,  # Invalid: Negative rooms
            status="Available",
            date_created=100.0
        )

def test_apartment_empty_code_fails():
    """
    Test that an apartment cannot be created with an empty unit code.
    """
    with pytest.raises(ValueError):
        apt = Apartment(
            apartment_id=3,
            location_id=101,
            unit_code="   ",  # Invalid: Blank/Empty spaces
            apt_type="Studio",
            monthly_rent=500.00,
            rooms=1,
            status="Available",
            date_created=100.0
        )

def test_user_empty_name_fails():
    """
    Test that a user cannot be created with a blank name.
    """
    with pytest.raises(ValueError):
        user = User(
            user_id=2,
            location_id=101,
            full_name="",  # Invalid: Empty name
            email="jane@example.com",
            password_hash="pass123",
            is_staff=False,
            date_created=100.0,
            is_active=True
        )