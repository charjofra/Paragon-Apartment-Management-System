CREATE DATABASE IF NOT EXISTS paragon_apartment_management_system
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE paragon_apartment_management_system;

-- 1) Locations
CREATE TABLE locations (
  location_id INT AUTO_INCREMENT PRIMARY KEY,
  city        VARCHAR(100) NOT NULL,
  address     VARCHAR(255) NULL,
  date_created  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_location_city_address (city, address)
);

-- 2) Users
CREATE TABLE users (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  location_id   INT NULL,
  full_name     VARCHAR(150) NOT NULL,
  email         VARCHAR(190) NOT NULL,
  phone         VARCHAR(50) NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_staff       TINYINT(1) NOT NULL DEFAULT 0,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  date_created    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_users_location
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
    ON DELETE SET NULL,

  UNIQUE KEY uq_users_email (email)
);

-- 3) Staff
CREATE TABLE staff (
  staff_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  role ENUM('FRONT_DESK','FINANCE_MANAGER','MAINTENANCE_STAFF','ADMINISTRATOR','MANAGER') NOT NULL,

  CONSTRAINT fk_staff_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE,

  UNIQUE KEY uq_staff_user (user_id)
);

-- 4) Tenants
CREATE TABLE tenants (
  tenant_id     INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  ni_number     VARCHAR(20) NOT NULL,
  occupation    VARCHAR(150) NULL,
  references_txt TEXT NULL,
  requirements  VARCHAR(255) NULL,
  created_by_staff_id INT NULL,
  date_created    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_tenants_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE,

  CONSTRAINT fk_tenants_created_by
    FOREIGN KEY (created_by_staff_id) REFERENCES staff(staff_id)
    ON DELETE SET NULL,

  UNIQUE KEY uq_tenants_ni (ni_number)
);

-- 5) Apartments
CREATE TABLE apartments (
  apartment_id  INT AUTO_INCREMENT PRIMARY KEY,
  location_id   INT NOT NULL,
  unit_code     VARCHAR(50) NOT NULL,
  apt_type      VARCHAR(80) NOT NULL,
  monthly_rent  DECIMAL(10,2) NOT NULL,
  rooms         INT NOT NULL,
  status ENUM('VACANT','OCCUPIED','MAINTENANCE') NOT NULL DEFAULT 'VACANT',
  date_created    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_apartments_location
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
    ON DELETE RESTRICT,

  UNIQUE KEY uq_apartments_unit (location_id, unit_code)
);

-- 6) Leases
CREATE TABLE leases (
  lease_id      INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  apartment_id  INT NOT NULL,
  start_date    DATE NOT NULL,
  end_date      DATE NOT NULL,
  monthly_rent  DECIMAL(10,2) NOT NULL,
  status ENUM('ACTIVE','ENDED','TERMINATION_REQUESTED') NOT NULL DEFAULT 'ACTIVE',

  -- Early termination: 1 month notice + 5% monthly rent penalty (calculated in app)
  early_leave_notice_date DATE NULL,
  early_leave_requested_end DATE NULL,
  early_leave_penalty DECIMAL(10,2) NULL,

  created_by_user_id INT NULL,
  date_created    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

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

CREATE INDEX idx_leases_apartment_status_dates ON leases(apartment_id, status, start_date, end_date);
CREATE INDEX idx_leases_tenant_status_dates ON leases(tenant_id, status, start_date, end_date);

-- 7) Complaints
CREATE TABLE complaints (
  complaint_id  INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  lease_id      INT NULL,
  date_created    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
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

-- 8) Maintenance requests
CREATE TABLE maintenance_requests (
  request_id    INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  apartment_id  INT NOT NULL,
  lease_id      INT NULL,
  date_created    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  description   TEXT NOT NULL,
  priority ENUM('LOW','MEDIUM','HIGH','URGENT') NOT NULL DEFAULT 'MEDIUM',
  status ENUM('REPORTED','TRIAGED','SCHEDULED','IN_PROGRESS','RESOLVED','CLOSED') NOT NULL DEFAULT 'REPORTED',
  scheduled_at  DATETIME NULL,

  assigned_to_user_id INT NULL,      -- maintenance staff
  registered_by_user_id INT NULL,    -- front desk/admin (optional)

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

-- 9) Maintenance resolutions (0..1 per request)
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

-- 10) Invoices
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

-- 11) Payments
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

-- 12) Notifications
CREATE TABLE notifications (
  notification_id INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id   INT NULL,
  user_id     INT NULL,
  type ENUM('LATE_PAYMENT','MAINTENANCE_UPDATE','LEASE_UPDATE','GENERAL') NOT NULL,
  message     VARCHAR(500) NOT NULL,
  date_created  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sent_at     DATETIME NULL,

  CONSTRAINT fk_notif_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
    ON DELETE CASCADE,

  CONSTRAINT fk_notif_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE
);

-- 13) Audit logs
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

-- -------------------------
-- Seed data (WORKING)
-- -------------------------
START TRANSACTION;

INSERT INTO locations (city, address) VALUES
('Bristol', '123 Filton Avenue'),
('London', '12 Oxford Street');

-- Demo hash placeholder so the SQL seed runs.
-- Replace in your app with real bcrypt hashes.
SET @DEMO_HASH = '$2b$12$LoKOunU3tubtqW8Dumdr..xvz3jmGyik6M1VT2UPvldqqEmHWqc3i'; -- password123

-- 1. Create the base User accounts
INSERT INTO users (location_id, full_name, email, password_hash, is_staff) VALUES
(1, 'John Doe',          'admin@paragon.com',       @DEMO_HASH, 1), -- user_id 1
(1, 'Jane Smith',        'manager@paragon.com',     @DEMO_HASH, 1), -- user_id 2
(1, 'Frank Desk',        'frontdesk@paragon.com',   @DEMO_HASH, 1), -- user_id 3
(1, 'Fiona Finance',     'finance@paragon.com',     @DEMO_HASH, 1), -- user_id 4
(1, 'Manny Maintenance', 'maintenance@paragon.com', @DEMO_HASH, 1), -- user_id 5
(2, 'John Smith',        'john@email.com',          @DEMO_HASH, 0); -- user_id 6 (Tenant)

-- 2. Create the Staff profiles (linking to user_id 1 through 5)
INSERT INTO staff (user_id, role) VALUES
(1, 'ADMINISTRATOR'),     -- staff_id 1
(2, 'MANAGER'),           -- staff_id 2
(3, 'FRONT_DESK'),        -- staff_id 3
(4, 'FINANCE_MANAGER'),   -- staff_id 4
(5, 'MAINTENANCE_STAFF'); -- staff_id 5

-- 3. Create the Tenant profile (linking to user_id 6)
INSERT INTO tenants (user_id, ni_number, created_by_staff_id) VALUES
(6, 'AB123456C', 3); -- Maps to John Smith, created by Frank Desk (staff_id 3)

COMMIT;