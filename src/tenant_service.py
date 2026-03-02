from db_utils import execute_read, execute_write
from models.payment import Payment
from models.maintenance_request import MaintenanceRequest
from models.complaint import Complaint
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

    def get_unpaid_invoices(self) -> List[Dict[str, Any]]:
        """
        Fetches unpaid invoices for this tenant to identify late payments.
        """
        query = """
            SELECT i.invoice_id, i.amount as amount_due, i.due_date, i.status
            FROM invoices i
            JOIN leases l ON i.lease_id = l.lease_id
            WHERE l.tenant_id = %s AND i.status = 'UNPAID'
            ORDER BY i.due_date ASC
        """
        return execute_read(query, (self.tenant_id,))

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
