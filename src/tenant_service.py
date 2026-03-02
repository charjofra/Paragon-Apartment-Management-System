from db_utils import execute_read, execute_write
from models import Payment, MaintenanceRequest, Complaint
from typing import List, Dict, Any

class TenantService:
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id

    def get_tenant_details(self) -> Dict[str, Any]:
        """
        Fetches full details for the tenant profile.
        """
        query = """
            SELECT ni_number, occupation, references_txt, requirements
            FROM tenants
            WHERE tenant_id = %s
        """
        results = execute_read(query, (self.tenant_id,))
        return results[0] if results else {}

    def get_payment_history(self) -> List[Dict[str, Any]]:
        """
        Fetches all payments made by this tenant.
        """
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
        """
        Fetches unpaid invoices. If overdue_only is True, filters for past due date.
        """
        base_query = """
            SELECT i.invoice_id, i.amount as amount_due, i.due_date, i.status
            FROM invoices i
            JOIN leases l ON i.lease_id = l.lease_id
            WHERE l.tenant_id = %s 
        """
        
        if overdue_only:
            base_query += " AND i.status IN ('UNPAID', 'LATE') AND i.due_date < CURDATE()"
        else:
            base_query += " AND i.status = 'UNPAID'"
            
        base_query += " ORDER BY i.due_date ASC"
        
        return execute_read(base_query, (self.tenant_id,))

    def get_maintenance_requests(self) -> List[Dict[str, Any]]:
        """
        Fetches maintenance requests submitted by this tenant.
        """
        query = """
            SELECT request_id, description, status, date_created, priority
            FROM maintenance_requests
            WHERE tenant_id = %s
            ORDER BY date_created DESC
        """
        return execute_read(query, (self.tenant_id,))

    def get_active_lease_info(self) -> List[Dict[str, Any]]:
        """
        Fetches active lease information including apartment details.
        """
        query = """
            SELECT l.lease_id, l.apartment_id, a.unit_code, loc.address, loc.city
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            JOIN locations loc ON a.location_id = loc.location_id
            WHERE l.tenant_id = %s AND l.status = 'ACTIVE'
        """
        return execute_read(query, (self.tenant_id,))

    def submit_maintenance_request(self, description: str, priority: str, apartment_id: int) -> bool:
        """
        Submits a new maintenance request.
        """
        # First, find the active lease for this tenant and apartment
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
            VALUES (%s, %s, %s, %s, %s, 'OPEN')
        """
        execute_write(insert_query, (self.tenant_id, apartment_id, lease_id, description, priority))
        return True

    def submit_complaint(self, description: str) -> bool:
        """
        Submits a new complaint.
        """
        # Get active lease
        lease_query = """
            SELECT lease_id FROM leases 
            WHERE tenant_id = %s AND status = 'ACTIVE'
            LIMIT 1
        """
        leases = execute_read(lease_query, (self.tenant_id,))
        if not leases:
            return False # No active lease found
            
        lease_id = leases[0]['lease_id']

        insert_query = """
            INSERT INTO complaints (tenant_id, lease_id, description, status)
            VALUES (%s, %s, %s, 'OPEN')
        """
        execute_write(insert_query, (self.tenant_id, lease_id, description))
        return True

    def pay_invoice(self, invoice_id: int, amount: float) -> bool:
        """
        Records a payment for an invoice and updates invoice status.
        """
        # 1. Record the payment
        payment_query = """
            INSERT INTO payments (invoice_id, amount_paid, method, recorded_by_user_id)
            VALUES (%s, %s, 'CARD', %s)
        """
        # We need the user_id associated with this tenant for recorded_by_user_id
        # For simplicity, we can fetch it or just pass None if self.tenant_id is strictly tenant context
        # But wait, self.tenant_id is the tenant ID, not user ID. 
        # Let's fetch the user_id for this tenant.
        user_query = "SELECT user_id FROM tenants WHERE tenant_id = %s"
        users = execute_read(user_query, (self.tenant_id,))
        user_id = users[0]['user_id'] if users else None

        execute_write(payment_query, (invoice_id, amount, user_id))

        # 2. Update invoice status
        # Check if fully paid? For simplistic logic, assume full payment marks as PAID.
        invoice_query = """
            UPDATE invoices SET status = 'PAID' WHERE invoice_id = %s
        """
        execute_write(invoice_query, (invoice_id,))
        return True
