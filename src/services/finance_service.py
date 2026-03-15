from utils.db_utils import execute_read, execute_write
from datetime import datetime, date

class FinanceService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_financial_stats(self):
        """Returns collected vs pending rent and other stats."""
        # Pending: Sum of all UNPAID or LATE invoices
        sql_pending = """
            SELECT SUM(amount) as pending_total, COUNT(*) as pending_count 
            FROM invoices WHERE status IN ('UNPAID', 'LATE')
        """
        pending_res = execute_read(sql_pending)
        pending_total = pending_res[0]['pending_total'] or 0.0
        pending_count = pending_res[0]['pending_count']

        # Collected: Sum of all payments
        sql_collected = "SELECT SUM(amount_paid) as collected_total FROM payments"
        collected_res = execute_read(sql_collected)
        collected_total = collected_res[0]['collected_total'] or 0.0

        # Overdue count
        sql_overdue = "SELECT COUNT(*) as count FROM invoices WHERE status = 'LATE'"
        overdue_res = execute_read(sql_overdue)
        overdue_count = overdue_res[0]['count']
        
        # Maintenance Costs
        sql_maint = "SELECT SUM(cost) as total_cost FROM maintenance_resolutions"
        maint_res = execute_read(sql_maint)
        maint_total = maint_res[0]['total_cost'] or 0.0

        return {
            "pending_total": float(pending_total),
            "pending_count": pending_count,
            "collected_total": float(collected_total),
            "overdue_count": overdue_count,
            "maintenance_total": float(maint_total)
        }

    def get_all_invoices(self, status=None):
        sql = """
            SELECT i.invoice_id, i.amount, i.status, i.due_date, i.issued_at, 
                   t.ni_number, u.full_name as tenant_name,
                   a.unit_code, l.monthly_rent
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.tenant_id
            JOIN users u ON t.user_id = u.user_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
        """
        params = []
        if status:
            sql += " WHERE i.status = %s"
            params.append(status)
        
        sql += " ORDER BY i.due_date DESC"
        return execute_read(sql, tuple(params))

    def get_all_payments(self):
        sql = """
            SELECT p.payment_id, p.amount_paid, p.paid_at, p.method,
                   i.invoice_id, u.full_name as tenant_name, a.unit_code
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.invoice_id
            JOIN tenants t ON i.tenant_id = t.tenant_id
            JOIN users u ON t.user_id = u.user_id
            JOIN leases l ON i.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            ORDER BY p.paid_at DESC
        """
        return execute_read(sql)

    def record_payment(self, invoice_id, amount, method):
        # 1. Insert payment
        if not amount or float(amount) <= 0:
            raise ValueError("Amount must be positive.")
            
        sql_pay = """
            INSERT INTO payments (invoice_id, amount_paid, method, recorded_by_user_id)
            VALUES (%s, %s, %s, %s)
        """
        # Pass parameters as a tuple directly to execute_write
        execute_write(sql_pay, (invoice_id, amount, method, self.user_id))

        # 2. Check if fully paid and update invoice status
        sql_check = "SELECT amount FROM invoices WHERE invoice_id = %s"
        inv_res = execute_read(sql_check, (invoice_id,))
        if not inv_res:
            return False
            
        total_due = float(inv_res[0]['amount'])

        sql_paid = "SELECT SUM(amount_paid) as total FROM payments WHERE invoice_id = %s"
        paid_res = execute_read(sql_paid, (invoice_id,))
        total_paid = float(paid_res[0]['total'] or 0)

        if total_paid >= total_due:
            execute_write("UPDATE invoices SET status='PAID' WHERE invoice_id=%s", (invoice_id,))
        
        return True

    def generate_monthly_invoices(self):
        """Finds all active leases without an invoice for the current month and creates one."""
        current_month = date.today().replace(day=1)
        
        # Get active leases
        sql_leases = """
            SELECT lease_id, tenant_id, apartment_id, monthly_rent, start_date 
            FROM leases WHERE status = 'ACTIVE'
        """
        leases = execute_read(sql_leases)
        
        generated_count = 0
        
        for lease in leases:
            # Check if invoice exists for this month/year
            sql_check = """
                SELECT invoice_id FROM invoices 
                WHERE lease_id = %s AND YEAR(issued_at) = %s AND MONTH(issued_at) = %s
            """
            exists = execute_read(sql_check, (lease['lease_id'], current_month.year, current_month.month))
            
            if not exists:
                # Create invoice
                # Due date is +14 days from now? Or end of month? Let's say due in 14 days.
                due_date = date.today().replace(day=min(28, date.today().day + 14))
                
                sql_insert = """
                    INSERT INTO invoices (tenant_id, lease_id, amount, due_date, status)
                    VALUES (%s, %s, %s, %s, 'UNPAID')
                """
                execute_write(sql_insert, (lease['tenant_id'], lease['lease_id'], lease['monthly_rent'], due_date))
                generated_count += 1
                
        return generated_count

    def send_late_notifications(self):
        """Sends notifications for all LATE invoices that haven't been notified recently."""
        # Find late invoices
        sql_late = """
            SELECT i.invoice_id, i.tenant_id, i.amount, i.due_date 
            FROM invoices i
            WHERE i.status = 'LATE' OR (i.status = 'UNPAID' AND i.due_date < CURDATE())
        """
        late_invoices = execute_read(sql_late)
        
        count = 0
        for inv in late_invoices:
            # Update status to LATE if it was UNPAID
            execute_write("UPDATE invoices SET status='LATE' WHERE invoice_id=%s", (inv['invoice_id'],))
            
            # Create notification
            msg = f"URGENT: Your rent payment of £{inv['amount']} was due on {inv['due_date']}."
            sql_notif = """
                INSERT INTO notifications (tenant_id, user_id, type, message, sent_at)
                VALUES (%s, %s, 'LATE_PAYMENT', %s, NOW())
            """
            execute_write(sql_notif, (inv['tenant_id'], self.user_id, msg))
            
            # Update last_notified_at
            execute_write("UPDATE invoices SET last_notified_at=NOW() WHERE invoice_id=%s", (inv['invoice_id'],))
            count += 1
            
        return count
    
    def get_maintenance_costs_data(self):
        """Returns monthly maintenance costs for the last 6 months."""
        sql = """
            SELECT DATE_FORMAT(resolved_at, '%Y-%m') as month, SUM(cost) as total_cost
            FROM maintenance_resolutions
            WHERE resolved_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY month ASC
        """
        return execute_read(sql)

    def get_revenue_data(self):
        """Returns monthly revenue for the last 6 months."""
        sql = """
            SELECT DATE_FORMAT(paid_at, '%Y-%m') as month, SUM(amount_paid) as total_paid
            FROM payments
            WHERE paid_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY month ASC
        """
        return execute_read(sql)
