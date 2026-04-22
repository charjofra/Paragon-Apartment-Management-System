# Paragon-Apartment-Management-System
Group project for Advanced Software Development and Systems Development.

### Install dependencies
```
pip install mysql-connector-python
pip install bcrypt
pip install python-dotenv
pip install pillow
pip install customtkinter
pip install pytest
```

### Running Tests
To run the automated tests for models and services, ensure `pytest` is installed and run the following command in the project root:
```bash
python -m pytest tests/
```


### Make a .env file in the root and insert the following
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=paragon_apartment_management_system
```
Change DB_PASSWORD to your database password.

To start the software, run "main.py".

### Dummy Data from the schema
```
Email                       Password        Role
admin@paragon.com           password123     Admin
manager@paragon.com         password123     Manager
frontdesk@paragon.com       password123     Fornt Desk
finance@paragon.com         password123     Finance Manager
maintenance@paragon.com     password123     Maintenance Staff
john@email.com              password123     Tenant
```
