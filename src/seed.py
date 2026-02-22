from auth import create_user

if __name__ == "__main__":
    admin_id = create_user(
        full_name="Test Admin",
        email="admin@paragon.com",
        password="AdminPassword123!",
        role="ADMINISTRATOR",
        location_id=1
    )

    print("Admin created with ID:", admin_id)