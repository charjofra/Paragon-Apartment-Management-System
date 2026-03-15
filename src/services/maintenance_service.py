from utils.db_utils import execute_read, execute_write
from typing import List, Dict, Any, Optional


class MaintenanceService:
    """Service layer for the Maintenance Staff dashboard."""

    def __init__(self, user_id: int, location_id: int):
        self.user_id = user_id
        self.location_id = location_id

    # ── Overview stats ────────────────────────────────────────────────

    def get_overview_stats(self) -> Dict[str, Any]:
        total = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s""",
            (self.location_id,),
        )
        open_reqs = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND mr.status NOT IN ('RESOLVED','CLOSED')""",
            (self.location_id,),
        )
        my_assigned = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND mr.assigned_to_user_id = %s
                 AND mr.status NOT IN ('RESOLVED','CLOSED')""",
            (self.location_id, self.user_id),
        )
        scheduled = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND mr.status = 'SCHEDULED'""",
            (self.location_id,),
        )
        resolved = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND mr.status IN ('RESOLVED','CLOSED')""",
            (self.location_id,),
        )
        urgent = execute_read(
            """SELECT COUNT(*) AS cnt FROM maintenance_requests mr
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s AND mr.priority = 'URGENT'
                 AND mr.status NOT IN ('RESOLVED','CLOSED')""",
            (self.location_id,),
        )
        return {
            "total": total[0]["cnt"] if total else 0,
            "open": open_reqs[0]["cnt"] if open_reqs else 0,
            "my_assigned": my_assigned[0]["cnt"] if my_assigned else 0,
            "scheduled": scheduled[0]["cnt"] if scheduled else 0,
            "resolved": resolved[0]["cnt"] if resolved else 0,
            "urgent": urgent[0]["cnt"] if urgent else 0,
        }

    # ── Request queries ───────────────────────────────────────────────

    def get_my_requests(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT mr.request_id, u.full_name AS tenant_name, a.unit_code,
                      mr.description, mr.priority, mr.status, mr.date_created,
                      mr.scheduled_at, assigned.full_name AS assigned_to
               FROM maintenance_requests mr
               JOIN tenants t ON mr.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               LEFT JOIN users assigned ON mr.assigned_to_user_id = assigned.user_id
               WHERE a.location_id = %s AND mr.assigned_to_user_id = %s
               ORDER BY FIELD(mr.priority,'URGENT','HIGH','MEDIUM','LOW'),
                        mr.date_created DESC""",
            (self.location_id, self.user_id),
        )

    def get_all_requests(self) -> List[Dict[str, Any]]:
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
               ORDER BY FIELD(mr.priority,'URGENT','HIGH','MEDIUM','LOW'),
                        mr.date_created DESC""",
            (self.location_id,),
        )

    def get_scheduled_requests(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT mr.request_id, u.full_name AS tenant_name, a.unit_code,
                      mr.description, mr.priority, mr.status, mr.date_created,
                      mr.scheduled_at, assigned.full_name AS assigned_to
               FROM maintenance_requests mr
               JOIN tenants t ON mr.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               LEFT JOIN users assigned ON mr.assigned_to_user_id = assigned.user_id
               WHERE a.location_id = %s AND mr.status = 'SCHEDULED'
               ORDER BY mr.scheduled_at ASC""",
            (self.location_id,),
        )


    # ── Actions ───────────────────────────────────────────────────────

    def submit_maintenance_request(self, tenant_id: int, apartment_id: int,
                                   description: str, priority: str) -> None:
        """Called by staff (Front Desk) on behalf of a tenant."""
        execute_write(
            """INSERT INTO maintenance_requests
                   (tenant_id, apartment_id, description, priority, status,
                    registered_by_user_id)
               VALUES (%s, %s, %s, %s, 'REPORTED', %s)""",
            (tenant_id, apartment_id, description, priority, self.user_id),
        )

    def submit_complaint(self, tenant_id: int, description: str) -> None:
        """Called by staff (Front Desk) to log a complaint."""
        execute_write(
            """INSERT INTO complaints (tenant_id, description, status, handled_by_user_id)
               VALUES (%s, %s, 'OPEN', %s)""",
            (tenant_id, description, self.user_id),
        )

    def get_maintenance_staff(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT u.user_id, u.full_name
               FROM staff s
               JOIN users u ON s.user_id = u.user_id
               WHERE s.role = 'MAINTENANCE_STAFF' AND u.location_id = %s AND u.is_active = 1""",
            (self.location_id,),
        )

    def assign_request(self, request_id: int, staff_user_id: int) -> None:
        execute_write(
            """UPDATE maintenance_requests SET assigned_to_user_id = %s, status = 'TRIAGED'
               WHERE request_id = %s""",
            (staff_user_id, request_id),
        )

    def schedule_request(self, request_id: int, scheduled_at: str) -> None:
        execute_write(
            """UPDATE maintenance_requests SET scheduled_at = %s, status = 'SCHEDULED'
               WHERE request_id = %s""",
            (scheduled_at, request_id),
        )

    def start_work(self, request_id: int) -> None:
        execute_write(
            "UPDATE maintenance_requests SET status = 'IN_PROGRESS' WHERE request_id = %s",
            (request_id,),
        )

    def resolve_request(self, request_id: int, details: str,
                        hours: float, cost: float) -> None:
        execute_write(
            """INSERT INTO maintenance_resolutions
                      (request_id, resolved_at, resolution_details,
                       time_taken_hours, cost, recorded_by_user_id)
               VALUES (%s, NOW(), %s, %s, %s, %s)""",
            (request_id, details, hours, cost, self.user_id),
        )
        execute_write(
            "UPDATE maintenance_requests SET status = 'RESOLVED' WHERE request_id = %s",
            (request_id,),
        )

    def close_request(self, request_id: int) -> None:
        execute_write(
            "UPDATE maintenance_requests SET status = 'CLOSED' WHERE request_id = %s",
            (request_id,),
        )

    # ── Resolution history ────────────────────────────────────────────

    def get_resolution_history(self) -> List[Dict[str, Any]]:
        return execute_read(
            """SELECT a.unit_code, mr.description, mr.priority,
                      res.resolution_details, res.time_taken_hours, res.cost,
                      res.resolved_at, u.full_name AS tenant_name,
                      recorder.full_name AS resolved_by
               FROM maintenance_resolutions res
               JOIN maintenance_requests mr ON res.request_id = mr.request_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               JOIN tenants t ON mr.tenant_id = t.tenant_id
               JOIN users u ON t.user_id = u.user_id
               LEFT JOIN users recorder ON res.recorded_by_user_id = recorder.user_id
               WHERE a.location_id = %s
               ORDER BY res.resolved_at DESC""",
            (self.location_id,),
        )

    # ── Cost summary (for overview) ──────────────────────────────────

    def get_cost_summary(self) -> Dict[str, Any]:
        data = execute_read(
            """SELECT COALESCE(SUM(res.cost), 0) AS total_cost,
                      COALESCE(SUM(res.time_taken_hours), 0) AS total_hours,
                      COUNT(*) AS total_resolved
               FROM maintenance_resolutions res
               JOIN maintenance_requests mr ON res.request_id = mr.request_id
               JOIN apartments a ON mr.apartment_id = a.apartment_id
               WHERE a.location_id = %s""",
            (self.location_id,),
        )
        if data:
            return {
                "total_cost": float(data[0]["total_cost"]),
                "total_hours": float(data[0]["total_hours"]),
                "total_resolved": data[0]["total_resolved"],
            }
        return {"total_cost": 0.0, "total_hours": 0.0, "total_resolved": 0}
