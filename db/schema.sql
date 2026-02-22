    -- SQL database schema for a the apartment management system
    CREATE DATABASE IF NOT EXISTS paragon_apartment_management_system
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

    USE paragon_apartment_management_system;

    -- 1) Locations (for multi-city expansion)
    CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    city        VARCHAR(100) NOT NULL,
    address     VARCHAR(255) NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_location_city_address (city, address)
    );


<<<<<<< Updated upstream
=======
-- 2) Users (staff)
CREATE TABLE users (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  location_id   INT NULL,
  full_name     VARCHAR(150) NOT NULL,
  email         VARCHAR(190) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('FRONT_DESK','FINANCE_MANAGER','MAINTENANCE_STAFF','ADMINISTRATOR','MANAGER','TENANT') NOT NULL,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
>>>>>>> Stashed changes

    -- 2) Users (staff)
    CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    location_id   INT NULL,
    full_name     VARCHAR(150) NOT NULL,
    email         VARCHAR(190) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('FRONT_DESK','FINANCE_MANAGER','MAINTENANCE_STAFF','ADMINISTRATOR','MANAGER') NOT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ON DELETE SET NULL,
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_username (username)
    );

    -- 3) Tenants
    CREATE TABLE tenants (
    tenant_id     INT AUTO_INCREMENT PRIMARY KEY,
    ni_number     VARCHAR(20) NOT NULL,       -- store normalised format if possible
    full_name     VARCHAR(150) NOT NULL,
    phone         VARCHAR(50) NULL,
    email         VARCHAR(190) NULL,
    occupation    VARCHAR(150) NULL,
    references_txt TEXT NULL,
    requirements  VARCHAR(255) NULL,
    created_by_user_id INT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tenants_created_by
        FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL,
    UNIQUE KEY uq_tenants_ni (ni_number)
    );

    -- 4) Apartments
    CREATE TABLE apartments (
    apartment_id  INT AUTO_INCREMENT PRIMARY KEY,
    location_id   INT NOT NULL,
    unit_code     VARCHAR(50) NOT NULL,       -- e.g., "BAS-2B-12"
    apt_type      VARCHAR(80) NOT NULL,       -- e.g., "2-bed flat"
    monthly_rent  DECIMAL(10,2) NOT NULL,
    rooms         INT NOT NULL,
    status ENUM('VACANT','OCCUPIED','MAINTENANCE') NOT NULL DEFAULT 'VACANT',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_apartments_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ON DELETE RESTRICT,
    UNIQUE KEY uq_apartments_unit (location_id, unit_code)
    );

    -- 5) Leases (tenant-apartment relationship over time)
    CREATE TABLE leases (
    lease_id      INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id     INT NOT NULL,
    apartment_id  INT NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE NOT NULL,
    monthly_rent  DECIMAL(10,2) NOT NULL, -- snapshot at lease time
    status ENUM('ACTIVE','ENDED','TERMINATION_REQUESTED') NOT NULL DEFAULT 'ACTIVE',

    -- Early termination rule (1 month notice + 5% of monthly rent penalty)
    early_leave_notice_date DATE NULL,
    early_leave_requested_end DATE NULL,
    early_leave_penalty DECIMAL(10,2) NULL,

    created_by_user_id INT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_leases_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_leases_apartment
        FOREIGN KEY (apartment_id) REFERENCES apartments(apartment_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_leases_created_by
        FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL,

    CHECK (end_date > start_date)
    );

    -- Helpful index for occupancy / searching current leases
    CREATE INDEX idx_leases_apartment_status_dates ON leases(apartment_id, status, start_date, end_date);
    CREATE INDEX idx_leases_tenant_status_dates ON leases(tenant_id, status, start_date, end_date);

    -- 6) Complaints
    CREATE TABLE complaints (
    complaint_id  INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id     INT NOT NULL,
    lease_id      INT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description   TEXT NOT NULL,
    status ENUM('OPEN','IN_PROGRESS','RESOLVED','CLOSED') NOT NULL DEFAULT 'OPEN',
    handled_by_user_id INT NULL,

    CONSTRAINT fk_complaints_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_complaints_lease
        FOREIGN KEY (lease_id) REFERENCES leases(lease_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_complaints_handled_by
        FOREIGN KEY (handled_by_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
    );

    -- 7) Maintenance requests
    CREATE TABLE maintenance_requests (
    request_id    INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id     INT NOT NULL,
    apartment_id  INT NOT NULL,
    lease_id      INT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description   TEXT NOT NULL,
    priority ENUM('LOW','MEDIUM','HIGH','URGENT') NOT NULL DEFAULT 'MEDIUM',
    status ENUM('REPORTED','TRIAGED','SCHEDULED','IN_PROGRESS','RESOLVED','CLOSED') NOT NULL DEFAULT 'REPORTED',
    scheduled_at  DATETIME NULL,

    assigned_to_user_id INT NULL, -- maintenance staff
    registered_by_user_id INT NULL, -- front desk (optional)

    CONSTRAINT fk_mr_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_mr_apartment
        FOREIGN KEY (apartment_id) REFERENCES apartments(apartment_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_mr_lease
        FOREIGN KEY (lease_id) REFERENCES leases(lease_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_mr_assigned_to
        FOREIGN KEY (assigned_to_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_mr_registered_by
        FOREIGN KEY (registered_by_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
    );

    CREATE INDEX idx_mr_apartment_status ON maintenance_requests(apartment_id, status);
    CREATE INDEX idx_mr_assigned_status ON maintenance_requests(assigned_to_user_id, status);

    -- 8) Maintenance resolution (composition-like: 0..1 resolution per request)
    CREATE TABLE maintenance_resolutions (
    resolution_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id    INT NOT NULL,
    resolved_at   DATETIME NOT NULL,
    resolution_details TEXT NOT NULL,
    time_taken_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    cost         DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    recorded_by_user_id INT NULL,

    CONSTRAINT fk_res_request
        FOREIGN KEY (request_id) REFERENCES maintenance_requests(request_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_res_recorded_by
        FOREIGN KEY (recorded_by_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL,
    UNIQUE KEY uq_resolution_request (request_id)
    );

    -- 9) Invoices (emulate billing process)
    CREATE TABLE invoices (
    invoice_id    INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id     INT NOT NULL,
    lease_id      INT NOT NULL,
    issued_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date      DATE NOT NULL,
    amount        DECIMAL(10,2) NOT NULL,
    status ENUM('UNPAID','PAID','LATE','CANCELLED') NOT NULL DEFAULT 'UNPAID',
    last_notified_at DATETIME NULL,

    CONSTRAINT fk_inv_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_inv_lease
        FOREIGN KEY (lease_id) REFERENCES leases(lease_id)
        ON DELETE RESTRICT
    );

    CREATE INDEX idx_invoices_tenant_status ON invoices(tenant_id, status);
    CREATE INDEX idx_invoices_due_status ON invoices(due_date, status);

    -- 10) Payments
    CREATE TABLE payments (
    payment_id    INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id    INT NOT NULL,
    paid_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount_paid   DECIMAL(10,2) NOT NULL,
    method ENUM('CASH','CARD','BANK_TRANSFER','CHEQUE','OTHER') NOT NULL DEFAULT 'BANK_TRANSFER',
    recorded_by_user_id INT NULL,

    CONSTRAINT fk_pay_invoice
        FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_pay_recorded_by
        FOREIGN KEY (recorded_by_user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
    );

    CREATE INDEX idx_payments_invoice ON payments(invoice_id);

    -- 11) Notifications (late payment + maintenance scheduling)
    CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id   INT NULL,
    user_id     INT NULL,
    type ENUM('LATE_PAYMENT','MAINTENANCE_UPDATE','LEASE_UPDATE','GENERAL') NOT NULL,
    message     VARCHAR(500) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at     DATETIME NULL,

    CONSTRAINT fk_notif_tenant
        FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notif_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
    );

    -- 12) Audit logs
    CREATE TABLE audit_logs (
    audit_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NULL,
    happened_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action       VARCHAR(120) NOT NULL,
    resource_type VARCHAR(60) NOT NULL,
    resource_id  INT NULL,
    details      TEXT NULL,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
    );

    CREATE INDEX idx_audit_happened ON audit_logs(happened_at);

    START TRANSACTION;
    USE paragon_apartment_management_system;
    INSERT INTO locations (city, address) VALUES
    ('Springfield', '123 Main St'),
    ('Shelbyville', '456 Elm St');
    INSERT INTO paragon_apartment_management_system.users (first_name, last_name, email, role) VALUES
    ('John', 'Doe', 'john.doe@paragon.com', 'ADMINISTRATOR'),
    ('Jane', 'Smith', 'jane.smith@paragon.com', 'MANAGER'),