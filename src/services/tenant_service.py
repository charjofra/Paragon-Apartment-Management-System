from utils.db_utils import execute_read, execute_write
from models import Payment, MaintenanceRequest, Complaint
from typing import List, Dict, Any
from datetime import date, timedelta, datetime


class TenantService:
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id

    def get_tenant_details(self) -> Dict[str, Any]:
        query = """
            SELECT ni_number, occupation, references_txt, requirements
            FROM tenants
            WHERE tenant_id = %s
        """
        results = execute_read(query, (self.tenant_id,))
        return results[0] if results else {}

    # ── Lease Methods ─────────────────────────────────────────────────

    def get_all_leases(self) -> List[Dict[str, Any]]:
        query = """
            SELECT l.lease_id, l.start_date, l.end_date, l.monthly_rent, l.status,
                   l.early_leave_notice_date, l.early_leave_requested_end,
                   l.early_leave_penalty,
                   a.unit_code, a.apt_type, a.rooms, loc.city, loc.address
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN locations loc ON a.location_id = loc.location_id
            WHERE l.tenant_id = %s
            ORDER BY l.start_date DESC
        """
        return execute_read(query, (self.tenant_id,))

    def get_active_lease_info(self) -> List[Dict[str, Any]]:
        query = """
            SELECT l.lease_id, l.apartment_id, a.unit_code, loc.address, loc.city
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN locations loc ON a.location_id = loc.location_id
            WHERE l.tenant_id = %s AND l.status = 'ACTIVE'
        """
        return execute_read(query, (self.tenant_id,))

    def request_early_termination(self, lease_id: int) -> Dict[str, Any]:
        """Request early leave: 1-month notice, 5% monthly rent penalty."""
        lease_q = """
            SELECT lease_id, monthly_rent, status
            FROM leases WHERE lease_id = %s AND tenant_id = %s AND status = 'ACTIVE'
        """
        rows = execute_read(lease_q, (lease_id, self.tenant_id))
        if not rows:
            return {"success": False, "error": "No active lease found."}

        penalty = round(float(rows[0]["monthly_rent"]) * 0.05, 2)
        requested_end = date.today() + timedelta(days=30)

        # 1. Update Lease Status
        update_q = """
            UPDATE leases 
            SET status = 'TERMINATION_REQUESTED', early_leave_penalty = %s,
                early_leave_notice_date = CURDATE(), early_leave_requested_end = %s
            WHERE lease_id = %s
        """
        execute_write(update_q, (penalty, str(requested_end), lease_id))

        # 2. Create Penalty Invoice so it can be paid
        # We set the due date to the requested end date
        invoice_q = """
            INSERT INTO invoices (tenant_id, lease_id, amount, due_date, status)
            VALUES (%s, %s, %s, %s, 'UNPAID')
        """
        execute_write(invoice_q, (self.tenant_id, lease_id, penalty, str(requested_end)))
        
        return {"success": True, "penalty": penalty, "end_date": str(requested_end)}

    # ── Payment Methods ───────────────────────────────────────────────

    def get_payment_history(self) -> List[Dict[str, Any]]:
        query = """
            SELECT p.payment_id, p.paid_at, p.amount_paid, p.method, i.due_date
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN leases l ON i.lease_id = l.lease_id
            WHERE l.tenant_id = %s
            ORDER BY p.paid_at DESC
        """
        return execute_read(query, (self.tenant_id,))

    def get_unpaid_invoices(self, overdue_only: bool = False) -> List[Dict[str, Any]]:
        base_query = """
            SELECT i.invoice_id, i.amount as amount_due, i.due_date, i.status
            FROM invoices i
            JOIN leases l ON i.lease_id = l.lease_id
            WHERE l.tenant_id = %s 
        """
        if overdue_only:
            base_query += " AND i.status IN ('UNPAID', 'LATE') AND i.due_date < CURDATE()"
        else:
            base_query += " AND i.status IN ('UNPAID', 'LATE')"
        base_query += " ORDER BY i.due_date ASC"
        return execute_read(base_query, (self.tenant_id,))

    def get_monthly_payment_data(self) -> List[Dict[str, Any]]:
        """Monthly totals for the tenant's payment history chart."""
        query = """
            SELECT DATE_FORMAT(p.paid_at, '%%Y-%%m') AS month,
                   SUM(p.amount_paid) AS total
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN leases l ON i.lease_id = l.lease_id
            WHERE l.tenant_id = %s
            GROUP BY month
            ORDER BY month
        """
        return execute_read(query, (self.tenant_id,))

    def get_neighbour_comparison(self) -> Dict[str, Any]:
        """Compare this tenant's monthly payments against neighbours in the same building."""
        # Get tenant's current apartment location
        loc_q = """
            SELECT a.location_id
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE l.tenant_id = %s AND l.status = 'ACTIVE'
            LIMIT 1
        """
        loc_rows = execute_read(loc_q, (self.tenant_id,))
        if not loc_rows:
            return {"tenant": [], "neighbours": []}

        location_id = loc_rows[0]["location_id"]

        # Tenant's monthly payments
        t_q = """
            SELECT DATE_FORMAT(p.paid_at, '%%Y-%%m') AS month,
                   SUM(p.amount_paid) AS total
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN leases l ON i.lease_id = l.lease_id
            WHERE l.tenant_id = %s
            GROUP BY month ORDER BY month
        """
        tenant_data = execute_read(t_q, (self.tenant_id,))

        # Average of neighbours at same location (excluding this tenant)
        n_q = """
            SELECT DATE_FORMAT(p.paid_at, '%%Y-%%m') AS month,
                   AVG(monthly_total) AS avg_total
            FROM (
                SELECT p2.paid_at, l2.tenant_id,
                       SUM(p2.amount_paid) AS monthly_total
                FROM payments p2
                JOIN invoices i2 ON p2.invoice_id = i2.invoice_id
                JOIN leases l2 ON i2.lease_id = l2.lease_id
                JOIN apartments a2 ON l2.apartment_id = a2.apartment_id
                WHERE a2.location_id = %s AND l2.tenant_id != %s
                GROUP BY DATE_FORMAT(p2.paid_at, '%%Y-%%m'), l2.tenant_id
            ) AS sub
            JOIN payments p ON 1=1
            GROUP BY DATE_FORMAT(p.paid_at, '%%Y-%%m')
            ORDER BY month
        """
        # Simpler neighbour average query
        n_q = """
            SELECT DATE_FORMAT(p.paid_at, '%%Y-%%m') AS month,
                   ROUND(SUM(p.amount_paid) / COUNT(DISTINCT l.tenant_id), 2) AS avg_total
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE a.location_id = %s AND l.tenant_id != %s
            GROUP BY month ORDER BY month
        """
        neighbour_data = execute_read(n_q, (location_id, self.tenant_id))

        return {"tenant": tenant_data, "neighbours": neighbour_data}

    def get_late_payments_by_property(self) -> List[Dict[str, Any]]:
        """Late/overdue invoices per property at the tenant's location."""
        loc_q = """
            SELECT a.location_id
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE l.tenant_id = %s AND l.status = 'ACTIVE'
            LIMIT 1
        """
        loc_rows = execute_read(loc_q, (self.tenant_id,))
        if not loc_rows:
            return []

        location_id = loc_rows[0]["location_id"]
        
        query = """
            SELECT a.unit_code, COUNT(i.invoice_id) AS late_count
            FROM invoices i
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE a.location_id = %s
              AND (i.status = 'LATE' OR (i.status = 'UNPAID' AND i.due_date < CURDATE()))
            GROUP BY a.unit_code
            ORDER BY late_count DESC
        """
        return execute_read(query, (location_id,))

    def pay_invoice(self, invoice_id: int, amount: float, expiry_date: str) -> bool:
        try:
            # Convert MM/YY to the last day of that month for comparison
            exp_date = datetime.strptime(expiry_date, "%m/%y")
            # If the current date is after the expiry month
            if exp_date.year < datetime.now().year or \
               (exp_date.year == datetime.now().year and exp_date.month < datetime.now().month):
                return False, "That card is expired please use another" # Logic failed: Card is expired
        except ValueError:
            return False, "Invalid expiry date format. Please use MM/YY (e.g., 05/27)."
        
        user_query = "SELECT user_id FROM tenants WHERE tenant_id = %s"
        users = execute_read(user_query, (self.tenant_id,))
        user_id = users[0]['user_id'] if users else None

        payment_query = """
            INSERT INTO payments (invoice_id, amount_paid, method, recorded_by_user_id)
            VALUES (%s, %s, 'CARD', %s)
        """
        execute_write(payment_query, (invoice_id, amount, user_id))

        invoice_query = "UPDATE invoices SET status = 'PAID' WHERE invoice_id = %s"
        execute_write(invoice_query, (invoice_id,))
        return True, "Success"

    # ── Maintenance Methods ───────────────────────────────────────────

    def get_maintenance_requests(self) -> List[Dict[str, Any]]:
        query = """
            SELECT mr.request_id, mr.description, mr.status, mr.date_created,
                   mr.priority, mr.scheduled_at,
                   res.resolution_details, res.resolved_at,
                   res.time_taken_hours, res.cost
            FROM maintenance_requests mr
            LEFT JOIN maintenance_resolutions res ON mr.request_id = res.request_id
            WHERE mr.tenant_id = %s
            ORDER BY mr.date_created DESC
        """
        return execute_read(query, (self.tenant_id,))

    def submit_maintenance_request(self, description: str, priority: str, apartment_id: int) -> bool:
        lease_query = """
            SELECT lease_id FROM leases 
            WHERE tenant_id = %s AND apartment_id = %s AND status = 'ACTIVE'
            LIMIT 1
        """
        leases = execute_read(lease_query, (self.tenant_id, apartment_id))
        if not leases:
            return False
        lease_id = leases[0]['lease_id']
        insert_query = """
            INSERT INTO maintenance_requests (tenant_id, apartment_id, lease_id, description, priority, status)
            VALUES (%s, %s, %s, %s, %s, 'REPORTED')
        """
        execute_write(insert_query, (self.tenant_id, apartment_id, lease_id, description, priority))
        return True

    # ── Complaint Methods ─────────────────────────────────────────────

    def get_complaints(self) -> List[Dict[str, Any]]:
        query = """
            SELECT complaint_id, description, status, date_created
            FROM complaints
            WHERE tenant_id = %s
            ORDER BY date_created DESC
        """
        return execute_read(query, (self.tenant_id,))

    def submit_complaint(self, description: str) -> bool:
        lease_query = """
            SELECT lease_id FROM leases 
            WHERE tenant_id = %s AND status = 'ACTIVE'
            LIMIT 1
        """
        leases = execute_read(lease_query, (self.tenant_id,))
        if not leases:
            return False
        lease_id = leases[0]['lease_id']
        insert_query = """
            INSERT INTO complaints (tenant_id, lease_id, description, status)
            VALUES (%s, %s, %s, 'OPEN')
        """
        execute_write(insert_query, (self.tenant_id, lease_id, description))
        return True

    # ── Notification Methods ──────────────────────────────────────────

    def get_notifications(self) -> List[Dict[str, Any]]:
        query = """
            SELECT notification_id, type, message, date_created, sent_at
            FROM notifications
            WHERE tenant_id = %s
            ORDER BY date_created DESC
        """
        return execute_read(query, (self.tenant_id,))
