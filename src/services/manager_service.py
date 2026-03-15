from utils.db_utils import execute_read, execute_write
from typing import List, Dict, Any, Optional

class ManagerService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    # ── Location Management ──────────────────────────────────────────

    def get_all_locations(self) -> List[Dict[str, Any]]:
        return execute_read("SELECT location_id, city, address, date_created FROM locations ORDER BY city")

    def create_location(self, city: str, address: str) -> int:
        return execute_write(
            "INSERT INTO locations (city, address) VALUES (%s, %s)",
            (city, address)
        )

    # ── Performance Reports ──────────────────────────────────────────

    def get_aggregated_stats(self) -> Dict[str, Any]:
        """High-level stats across all locations."""
        total_locs = execute_read("SELECT COUNT(*) as cnt FROM locations")
        total_units = execute_read("SELECT COUNT(*) as cnt FROM apartments")
        occupancy = execute_read(
            """SELECT 
                (SELECT COUNT(*) FROM apartments WHERE status='OCCUPIED') / 
                NULLIF((SELECT COUNT(*) FROM apartments), 0) * 100 as rate"""
        )
        revenue = execute_read(
            "SELECT SUM(amount_paid) as total FROM payments WHERE paid_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        )

        return {
            "locations": total_locs[0]['cnt'],
            "units": total_units[0]['cnt'],
            "occupancy_rate": float(occupancy[0]['rate'] or 0),
            "monthly_revenue": float(revenue[0]['total'] or 0)
        }

    def get_location_performance(self, location_id: int) -> Dict[str, Any]:
        """Detailed stats for a specific location."""
        # Occupancy
        occ = execute_read(
            """SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='OCCUPIED' THEN 1 ELSE 0 END) as occupied
               FROM apartments WHERE location_id=%s""",
            (location_id,)
        )
        total = occ[0]['total'] or 0
        occupied = occ[0]['occupied'] or 0
        rate = (occupied / total * 100) if total > 0 else 0

        # Revenue (Last 30 days)
        rev = execute_read(
            """SELECT SUM(p.amount_paid) as total 
               FROM payments p
               JOIN invoices i ON p.invoice_id = i.invoice_id
               JOIN leases l ON i.lease_id = l.lease_id
               JOIN apartments a ON l.apartment_id = a.apartment_id
               WHERE a.location_id=%s AND p.paid_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)""",
            (location_id,)
        )
        
        # Maintenance Costs (Last 30 days)
        maint = execute_read(
            """SELECT SUM(res.cost) as total
               FROM maintenance_resolutions res
               JOIN maintenance_requests mr ON res.request_id = mr.request_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id=%s AND res.resolved_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)""",
            (location_id,)
        )

        return {
            "total_units": total,
            "occupied_units": occupied,
            "occupancy_rate": rate,
            "revenue": float(rev[0]['total'] or 0),
            "maintenance_costs": float(maint[0]['total'] or 0)
        }
