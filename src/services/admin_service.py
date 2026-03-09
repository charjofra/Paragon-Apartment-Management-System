import bcrypt
from utils.db_utils import execute_read, execute_write
from typing import List, Dict, Any, Optional


class AdminService:
    def __init__(self, user_id: int, location_id: int):
        self.user_id = user_id
        self.location_id = location_id

    # ── Overview / Stats ───────────────────────────────────────────────

    def get_overview_stats(self) -> Dict[str, Any]:
        total_apts = execute_read(
            "SELECT COUNT(*) AS cnt FROM apartments WHERE location_id = %s",
            (self.location_id,),
        )
        occupied = execute_read(
            "SELECT COUNT(*) AS cnt FROM apartments WHERE location_id = %s AND status = 'OCCUPIED'",
            (self.location_id,),
        )
        vacant = execute_read(
            "SELECT COUNT(*) AS cnt FROM apartments WHERE location_id = %s AND status = 'VACANT'",
            (self.location_id,),
        )
        maintenance_apt = execute_read(
            "SELECT COUNT(*) AS cnt FROM apartments WHERE location_id = %s AND status = 'MAINTENANCE'",
            (self.location_id,),
        )
        active_leases = execute_read(
            """SELECT COUNT(*) AS cnt FROM leases l
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND l.status = 'ACTIVE'""",
            (self.location_id,),
        )
        open_requests = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND mr.status NOT IN ('RESOLVED','CLOSED')""",
            (self.location_id,),
        )
        unpaid_invoices = execute_read(
            """SELECT COUNT(*) AS cnt, COALESCE(SUM(i.amount), 0) AS total
               FROM invoices i
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND i.status IN ('UNPAID','LATE')""",
            (self.location_id,),
        )
        open_complaints = execute_read(
            """SELECT COUNT(*) AS cnt FROM complaints c
               JOIN tenants t ON c.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               WHERE u.location_id = %s AND c.status IN ('OPEN','IN_PROGRESS')""",
            (self.location_id,),
        )
        return {
            "total_apartments": total_apts[0]["cnt"] if total_apts else 0,
            "occupied": occupied[0]["cnt"] if occupied else 0,
            "vacant": vacant[0]["cnt"] if vacant else 0,
            "maintenance_apt": maintenance_apt[0]["cnt"] if maintenance_apt else 0,
            "active_leases": active_leases[0]["cnt"] if active_leases else 0,
            "open_maintenance": open_requests[0]["cnt"] if open_requests else 0,
            "unpaid_invoices_count": unpaid_invoices[0]["cnt"] if unpaid_invoices else 0,
            "unpaid_invoices_total": float(unpaid_invoices[0]["total"]) if unpaid_invoices else 0.0,
            "open_complaints": open_complaints[0]["cnt"] if open_complaints else 0,
        }

    # ── User / Account Management ─────────────────────────────────────

    def get_all_users(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT u.user_id, u.full_name, u.email, u.phone, u.is_staff, u.is_active,
                      u.date_created, s.role, t.tenant_id
               FROM users u
               LEFT JOIN staff s ON u.user_id = s.user_id
               LEFT JOIN tenants t ON u.user_id = t.user_id
               WHERE u.location_id = %s
               ORDER BY u.date_created DESC""",
            (self.location_id,),
        )

    def create_staff_user(self, full_name: str, email: str, password: str,
                          phone: str, role: str) -> Optional[int]:
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = execute_write(
            """INSERT INTO users (location_id, full_name, email, phone, password_hash, is_staff)
               VALUES (%s, %s, %s, %s, %s, 1)""",
            (self.location_id, full_name, email, phone, pw_hash),
        )
        if user_id:
            execute_write(
                "INSERT INTO staff (user_id, role) VALUES (%s, %s)",
                (user_id, role),
            )
        return user_id

    def toggle_user_active(self, target_user_id: int, active: bool) -> None:
        execute_write(
            "UPDATE users SET is_active = %s WHERE user_id = %s",
            (1 if active else 0, target_user_id),
        )

    def update_user(self, target_user_id: int, full_name: str, email: str,
                    phone: str) -> None:
        execute_write(
            "UPDATE users SET full_name = %s, email = %s, phone = %s WHERE user_id = %s",
            (full_name, email, phone, target_user_id),
        )

    # ── Tenant Management ─────────────────────────────────────────────

    def get_all_tenants(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT t.tenant_id, u.user_id, u.full_name, u.email, u.phone,
                      t.ni_number, t.occupation, t.references_txt, t.requirements,
                      u.is_active, t.date_created
               FROM tenants t
               JOIN users u ON t.user_id = u.user_id
               WHERE u.location_id = %s
               ORDER BY t.date_created DESC""",
            (self.location_id,),
        )

    def register_tenant(self, full_name: str, email: str, password: str,
                        phone: str, ni_number: str, occupation: str,
                        references_txt: str, requirements: str) -> Optional[int]:
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = execute_write(
            """INSERT INTO users (location_id, full_name, email, phone, password_hash, is_staff)
               VALUES (%s, %s, %s, %s, %s, 0)""",
            (self.location_id, full_name, email, phone, pw_hash),
        )
        if user_id:
            # Fetch this admin's staff_id
            staff = execute_read(
                "SELECT staff_id FROM staff WHERE user_id = %s", (self.user_id,)
            )
            staff_id = staff[0]["staff_id"] if staff else None
            tenant_id = execute_write(
                """INSERT INTO tenants (user_id, ni_number, occupation, references_txt,
                                       requirements, created_by_staff_id)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, ni_number, occupation, references_txt, requirements, staff_id),
            )
            return tenant_id
        return None

    def update_tenant(self, tenant_id: int, full_name: str, email: str, phone: str,
                      occupation: str, references_txt: str, requirements: str) -> None:
        tenant = execute_read(
            "SELECT user_id FROM tenants WHERE tenant_id = %s", (tenant_id,)
        )
        if not tenant:
            return
        uid = tenant[0]["user_id"]
        execute_write(
            "UPDATE users SET full_name = %s, email = %s, phone = %s WHERE user_id = %s",
            (full_name, email, phone, uid),
        )
        execute_write(
            """UPDATE tenants SET occupation = %s, references_txt = %s, requirements = %s
               WHERE tenant_id = %s""",
            (occupation, references_txt, requirements, tenant_id),
        )

    def get_tenant_leases(self, tenant_id: int) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT l.lease_id, a.unit_code, loc.city, l.start_date, l.end_date,
                      l.monthly_rent, l.status, l.early_leave_notice_date,
                      l.early_leave_requested_end, l.early_leave_penalty
               FROM leases l
               JOIN apartments a ON l.apartment_id = a.apartment_id
               JOIN locations loc ON a.location_id = loc.location_id
               WHERE l.tenant_id = %s
               ORDER BY l.start_date DESC""",
            (tenant_id,),
        )

    def get_tenant_payments(self, tenant_id: int) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT p.payment_id, p.paid_at, p.amount_paid, p.method,
                      i.due_date, i.amount AS invoice_amount, i.status AS inv_status
               FROM payments p
               JOIN invoices i ON p.invoice_id = i.invoice_id
               WHERE i.tenant_id = %s
               ORDER BY p.paid_at DESC""",
            (tenant_id,),
        )

    def get_tenant_complaints(self, tenant_id: int) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT c.complaint_id, c.date_created, c.description, c.status
               FROM complaints c
               WHERE c.tenant_id = %s
               ORDER BY c.date_created DESC""",
            (tenant_id,),
        )

    # ── Apartment Management ──────────────────────────────────────────

    def get_all_apartments(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT a.apartment_id, a.unit_code, a.apt_type, a.monthly_rent,
                      a.rooms, a.status, loc.city, loc.address, a.date_created
               FROM apartments a
               JOIN locations loc ON a.location_id = loc.location_id
               WHERE a.location_id = %s
               ORDER BY a.unit_code""",
            (self.location_id,),
        )

    def add_apartment(self, unit_code: str, apt_type: str, monthly_rent: float,
                      rooms: int) -> Optional[int]:
        return execute_write(
            """INSERT INTO apartments (location_id, unit_code, apt_type, monthly_rent, rooms, status)
               VALUES (%s, %s, %s, %s, %s, 'VACANT')""",
            (self.location_id, unit_code, apt_type, monthly_rent, rooms),
        )

    def update_apartment(self, apartment_id: int, unit_code: str, apt_type: str,
                         monthly_rent: float, rooms: int, status: str) -> None:
        execute_write(
            """UPDATE apartments SET unit_code = %s, apt_type = %s, monthly_rent = %s,
                      rooms = %s, status = %s
               WHERE apartment_id = %s AND location_id = %s""",
            (unit_code, apt_type, monthly_rent, rooms, status, apartment_id, self.location_id),
        )

    def get_vacant_apartments(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT apartment_id, unit_code, apt_type, monthly_rent, rooms
               FROM apartments
               WHERE location_id = %s AND status = 'VACANT'
               ORDER BY unit_code""",
            (self.location_id,),
        )

    # ── Lease Management ──────────────────────────────────────────────

    def get_all_leases(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT l.lease_id, u.full_name AS tenant_name, a.unit_code,
                      loc.city, l.start_date, l.end_date, l.monthly_rent, l.status,
                      l.early_leave_notice_date, l.early_leave_requested_end,
                      l.early_leave_penalty, t.tenant_id
               FROM leases l
               JOIN tenants t ON l.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               JOIN locations loc ON a.location_id = loc.location_id
               WHERE a.location_id = %s
               ORDER BY l.start_date DESC""",
            (self.location_id,),
        )

    def create_lease(self, tenant_id: int, apartment_id: int, start_date: str,
                     end_date: str, monthly_rent: float) -> Optional[int]:
        lease_id = execute_write(
            """INSERT INTO leases (tenant_id, apartment_id, start_date, end_date,
                                  monthly_rent, status, created_by_user_id)
               VALUES (%s, %s, %s, %s, %s, 'ACTIVE', %s)""",
            (tenant_id, apartment_id, start_date, end_date, monthly_rent, self.user_id),
        )
        if lease_id:
            execute_write(
                "UPDATE apartments SET status = 'OCCUPIED' WHERE apartment_id = %s",
                (apartment_id,),
            )
        return lease_id

    def end_lease(self, lease_id: int) -> None:
        lease = execute_read(
            "SELECT apartment_id FROM leases WHERE lease_id = %s", (lease_id,)
        )
        execute_write(
            "UPDATE leases SET status = 'ENDED' WHERE lease_id = %s", (lease_id,)
        )
        if lease:
            execute_write(
                "UPDATE apartments SET status = 'VACANT' WHERE apartment_id = %s",
                (lease[0]["apartment_id"],),
            )

    def process_early_termination(self, lease_id: int, notice_date: str,
                                  requested_end: str, penalty: float) -> None:
        execute_write(
            """UPDATE leases SET status = 'TERMINATION_REQUESTED',
                      early_leave_notice_date = %s,
                      early_leave_requested_end = %s,
                      early_leave_penalty = %s
               WHERE lease_id = %s""",
            (notice_date, requested_end, penalty, lease_id),
        )

    # ── Payment & Billing ─────────────────────────────────────────────

    def get_all_invoices(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT i.invoice_id, u.full_name AS tenant_name, a.unit_code,
                      i.issued_at, i.due_date, i.amount, i.status
               FROM invoices i
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN tenants t ON i.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s
               ORDER BY i.due_date DESC""",
            (self.location_id,),
        )

    def create_invoice(self, tenant_id: int, lease_id: int, due_date: str,
                       amount: float) -> Optional[int]:
        return execute_write(
            """INSERT INTO invoices (tenant_id, lease_id, due_date, amount, status)
               VALUES (%s, %s, %s, %s, 'UNPAID')""",
            (tenant_id, lease_id, due_date, amount),
        )

    def record_payment(self, invoice_id: int, amount: float,
                       method: str) -> Optional[int]:
        pay_id = execute_write(
            """INSERT INTO payments (invoice_id, amount_paid, method, recorded_by_user_id)
               VALUES (%s, %s, %s, %s)""",
            (invoice_id, amount, method, self.user_id),
        )
        if pay_id:
            execute_write(
                "UPDATE invoices SET status = 'PAID' WHERE invoice_id = %s",
                (invoice_id,),
            )
        return pay_id

    def get_late_invoices(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT i.invoice_id, u.full_name AS tenant_name, a.unit_code,
                      i.due_date, i.amount, i.status
               FROM invoices i
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN tenants t ON i.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s
                 AND i.status IN ('UNPAID','LATE')
                 AND i.due_date < CURDATE()
               ORDER BY i.due_date ASC""",
            (self.location_id,),
        )

    def send_late_notification(self, tenant_id: int, message: str) -> Optional[int]:
        user = execute_read(
            "SELECT user_id FROM tenants WHERE tenant_id = %s", (tenant_id,)
        )
        user_id = user[0]["user_id"] if user else None
        return execute_write(
            """INSERT INTO notifications (tenant_id, user_id, type, message)
               VALUES (%s, %s, 'LATE_PAYMENT', %s)""",
            (tenant_id, user_id, message),
        )

    # ── Maintenance ───────────────────────────────────────────────────

    def get_all_maintenance_requests(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT mr.request_id, u.full_name AS tenant_name, a.unit_code,
                      mr.description, mr.priority, mr.status, mr.date_created,
                      mr.scheduled_at, assigned.full_name AS assigned_to
               FROM maintenance_requests mr
               JOIN tenants t ON mr.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               LEFT JOIN users assigned ON mr.assigned_to_user_id = assigned.user_id
               WHERE a.location_id = %s
               ORDER BY FIELD(mr.priority,'URGENT','HIGH','MEDIUM','LOW'), mr.date_created DESC""",
            (self.location_id,),
        )

    def get_maintenance_staff(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT u.user_id, u.full_name
               FROM staff s
               JOIN users u ON s.user_id = u.user_id
               WHERE s.role = 'MAINTENANCE_STAFF' AND u.location_id = %s AND u.is_active = 1""",
            (self.location_id,),
        )

    def assign_maintenance(self, request_id: int, staff_user_id: int) -> None:
        execute_write(
            """UPDATE maintenance_requests SET assigned_to_user_id = %s, status = 'TRIAGED'
               WHERE request_id = %s""",
            (staff_user_id, request_id),
        )

    def schedule_maintenance(self, request_id: int, scheduled_at: str) -> None:
        execute_write(
            """UPDATE maintenance_requests SET scheduled_at = %s, status = 'SCHEDULED'
               WHERE request_id = %s""",
            (scheduled_at, request_id),
        )

    def update_maintenance_status(self, request_id: int, status: str) -> None:
        execute_write(
            "UPDATE maintenance_requests SET status = %s WHERE request_id = %s",
            (status, request_id),
        )

    def resolve_maintenance(self, request_id: int, details: str,
                            hours: float, cost: float) -> None:
        execute_write(
            """INSERT INTO maintenance_resolutions
                      (request_id, resolved_at, resolution_details, time_taken_hours, cost, recorded_by_user_id)
               VALUES (%s, NOW(), %s, %s, %s, %s)""",
            (request_id, details, hours, cost, self.user_id),
        )
        execute_write(
            "UPDATE maintenance_requests SET status = 'RESOLVED' WHERE request_id = %s",
            (request_id,),
        )

    # ── Reports ───────────────────────────────────────────────────────

    def get_occupancy_report(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT a.unit_code, a.apt_type, a.rooms, a.status, a.monthly_rent,
                      loc.city, loc.address
               FROM apartments a
               JOIN locations loc ON a.location_id = loc.location_id
               WHERE a.location_id = %s
               ORDER BY a.status, a.unit_code""",
            (self.location_id,),
        )

    def get_financial_summary(self) -> Dict[str, Any]:
        collected = execute_read(
            """SELECT COALESCE(SUM(p.amount_paid), 0) AS total
               FROM payments p
               JOIN invoices i ON p.invoice_id = i.invoice_id
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s""",
            (self.location_id,),
        )
        pending = execute_read(
            """SELECT COALESCE(SUM(i.amount), 0) AS total
               FROM invoices i
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND i.status IN ('UNPAID','LATE')""",
            (self.location_id,),
        )
        monthly = execute_read(
            """SELECT DATE_FORMAT(p.paid_at, '%%Y-%%m') AS month,
                      SUM(p.amount_paid) AS total
               FROM payments p
               JOIN invoices i ON p.invoice_id = i.invoice_id
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s
               GROUP BY month ORDER BY month DESC LIMIT 12""",
            (self.location_id,),
        )
        return {
            "total_collected": float(collected[0]["total"]) if collected else 0.0,
            "total_pending": float(pending[0]["total"]) if pending else 0.0,
            "monthly_breakdown": monthly,
        }

    def get_maintenance_cost_report(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT a.unit_code, mr.description, res.resolution_details,
                      res.time_taken_hours, res.cost, res.resolved_at
               FROM maintenance_resolutions res
               JOIN maintenance_requests mr ON res.request_id = mr.request_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s
               ORDER BY res.resolved_at DESC""",
            (self.location_id,),
        )

    def get_expiring_leases(self, days: int = 30) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT l.lease_id, u.full_name AS tenant_name, a.unit_code,
                      l.end_date, l.monthly_rent, l.status
               FROM leases l
               JOIN tenants t ON l.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND l.status = 'ACTIVE'
                 AND l.end_date <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
               ORDER BY l.end_date ASC""",
            (self.location_id, days),
        )

    # ── Complaints ────────────────────────────────────────────────────

    def get_all_complaints(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT c.complaint_id, u.full_name AS tenant_name, a.unit_code,
                      c.date_created, c.description, c.status
               FROM complaints c
               JOIN tenants t ON c.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               LEFT JOIN leases l ON c.lease_id = l.lease_id
               LEFT JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE u.location_id = %s
               ORDER BY c.date_created DESC""",
            (self.location_id,),
        )

    def update_complaint_status(self, complaint_id: int, status: str) -> None:
        execute_write(
            """UPDATE complaints SET status = %s, handled_by_user_id = %s
               WHERE complaint_id = %s""",
            (status, self.user_id, complaint_id),
        )
