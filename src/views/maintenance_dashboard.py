import customtkinter as ctk
from models.user import User
from services.maintenance_service import MaintenanceService
from typing import TYPE_CHECKING
from tkinter import messagebox
from datetime import date, timedelta

if TYPE_CHECKING:
    from views.gui import App

# ── Single colour map for every status / priority value ───────────

C = {
    "OPEN":        "#3498db",
    "IN_PROGRESS": "#f1c40f",
    "RESOLVED":    "#2ecc71",
    "CLOSED":      "#e74c3c",
    "REPORTED":    "#3498db",
    "TRIAGED":     "#9b59b6",
    "SCHEDULED":   "#f39c12",
    "LOW":    "#2ecc71",
    "MEDIUM": "#f39c12",
    "HIGH":   "#e67e22",
    "URGENT": "#e74c3c",
}
_GREY = "#95a5a6"

_DISPLAY_OVERRIDES = {
    "TRIAGED": "Assigned",
}


def _humanise(text: str) -> str:
    if text in _DISPLAY_OVERRIDES:
        return _DISPLAY_OVERRIDES[text]
    return text.replace("_", " ").title()


def _uk_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        value_str = value
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                from datetime import datetime
                dt = datetime.strptime(value_str[:len(fmt.replace("%", "0"))], fmt)
                return dt.strftime("%d/%m/%Y %H:%M" if " " in fmt else "%d/%m/%Y")
            except (ValueError, IndexError):
                continue
        return value_str
    return value.strftime("%d/%m/%Y")


class MaintenanceDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.service = MaintenanceService(user.user_id, user.location_id)

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        label = ctk.CTkLabel(
            self.header_frame,
            text=f"Maintenance Panel — {user.full_name}",
            font=("Arial", 20, "bold"),
        )
        label.pack(side="left", padx=20, pady=10)

        logout_btn = ctk.CTkButton(
            self.header_frame, text="Logout", command=parent.logout, width=80
        )
        logout_btn.pack(side="right", padx=20, pady=10)

        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_overview = self.tab_view.add("Overview")
        self.tab_my_requests = self.tab_view.add("My Requests")
        self.tab_all_requests = self.tab_view.add("All Requests")
        self.tab_schedule = self.tab_view.add("Schedule")
        self.tab_resolutions = self.tab_view.add("Resolutions")

        self.setup_overview_tab()
        self.setup_my_requests_tab()
        self.setup_all_requests_tab()
        self.setup_schedule_tab()
        self.setup_resolutions_tab()

    # ── helpers ────────────────────────────────────────────────────────

    def _clear(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _make_table(self, parent, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [120] * len(headers)
        hf = ctk.CTkFrame(parent)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=col_widths[i], anchor="w").pack(side="left", padx=5)
        for row in rows:
            rf = ctk.CTkFrame(parent)
            rf.pack(fill="x", pady=1)
            for i, val in enumerate(row):
                ctk.CTkLabel(rf, text=str(val), width=col_widths[i],
                             anchor="w").pack(side="left", padx=5)
        return hf

    @staticmethod
    def _status_badge(parent, text: str, colour: str, width: int = 110):
        badge = ctk.CTkFrame(parent, fg_color=colour, corner_radius=6,
                             width=width, height=26)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=5)
        ctk.CTkLabel(badge, text=_humanise(text), text_color="white",
                     font=("Arial", 11, "bold")).pack(expand=True)
        return badge

    @staticmethod
    def _priority_badge(parent, text: str, width: int = 80):
        colour = C.get(text, _GREY)
        badge = ctk.CTkFrame(parent, fg_color=colour, corner_radius=6,
                             width=width, height=26)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=5)
        ctk.CTkLabel(badge, text=_humanise(text), text_color="white",
                     font=("Arial", 11, "bold")).pack(expand=True)
        return badge

    # ── Overview ──────────────────────────────────────────────────────

    def setup_overview_tab(self):
        frame = self.tab_overview
        self._clear(frame)

        ctk.CTkLabel(frame, text="Dashboard Overview",
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        try:
            stats = self.service.get_overview_stats()
        except Exception:
            ctk.CTkLabel(frame, text="Unable to load overview.").pack(pady=20)
            return

        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=10)

        items = [
            ("Total Requests", stats["total"]),
            ("Open", stats["open"]),
            ("Assigned to Me", stats["my_assigned"]),
            ("Scheduled", stats["scheduled"]),
            ("Resolved / Closed", stats["resolved"]),
            ("Urgent Open", stats["urgent"]),
        ]
        for idx, (title, value) in enumerate(items):
            card = ctk.CTkFrame(cards_frame)
            card.grid(row=0, column=idx, padx=8, pady=5, sticky="nsew")
            cards_frame.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(8, 2))
            ctk.CTkLabel(card, text=str(value),
                         font=("Arial", 22, "bold")).pack(pady=(2, 8))

        # Cost summary
        try:
            costs = self.service.get_cost_summary()
        except Exception:
            costs = None

        if costs:
            cost_frame = ctk.CTkFrame(frame)
            cost_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(
                cost_frame,
                text=f"Total Maintenance Cost: £{costs['total_cost']:.2f}  |  "
                     f"Total Hours Logged: {costs['total_hours']:.1f}  |  "
                     f"Total Resolved: {costs['total_resolved']}",
                font=("Arial", 13, "bold"),
            ).pack(pady=8, padx=10)

    # ── My Requests ───────────────────────────────────────────────────

    def setup_my_requests_tab(self):
        frame = self.tab_my_requests
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_my_requests_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Requests Assigned to Me")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            requests = self.service.get_my_requests()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load requests.").pack(pady=20)
            return

        if not requests:
            ctk.CTkLabel(sf, text="No requests assigned to you.").pack(pady=20)
            return

        self._render_request_list(sf, requests, show_actions=True)

    # ── All Requests ──────────────────────────────────────────────────

    def setup_all_requests_tab(self):
        frame = self.tab_all_requests
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_all_requests_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="All Maintenance Requests")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            requests = self.service.get_all_requests()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load requests.").pack(pady=20)
            return

        if not requests:
            ctk.CTkLabel(sf, text="No maintenance requests found.").pack(pady=20)
            return

        self._render_request_list(sf, requests, show_actions=True)

    # ── Schedule tab ──────────────────────────────────────────────────

    def setup_schedule_tab(self):
        frame = self.tab_schedule
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_schedule_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Scheduled Maintenance")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            requests = self.service.get_scheduled_requests()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load schedule.").pack(pady=20)
            return

        if not requests:
            ctk.CTkLabel(sf, text="No scheduled maintenance.").pack(pady=20)
            return

        for req in requests:
            card = ctk.CTkFrame(sf, fg_color=("gray85", "gray17"))
            card.pack(fill="x", pady=4, padx=5)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=8, pady=(6, 2))

            ctk.CTkLabel(top, text=f"#{req['request_id']}",
                         font=("Arial", 11, "bold"), width=40).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(top, text=req["unit_code"],
                         font=("Arial", 11), width=60).pack(side="left", padx=5)
            ctk.CTkLabel(top, text=req["tenant_name"],
                         font=("Arial", 11), width=120).pack(side="left", padx=5)

            self._priority_badge(top, req["priority"])

            sched_text = f"Scheduled: {_uk_date(req['scheduled_at'])}" if req.get("scheduled_at") else "Not scheduled"
            ctk.CTkLabel(top, text=sched_text,
                         font=("Arial", 11, "bold")).pack(side="left", padx=10)

            assigned = req.get("assigned_to") or "Unassigned"
            ctk.CTkLabel(top, text=f"Assigned: {assigned}",
                         font=("Arial", 11)).pack(side="right", padx=5)

            ctk.CTkLabel(card, text=req["description"], anchor="w",
                         wraplength=550, justify="left",
                         font=("Arial", 12)).pack(fill="x", padx=10, pady=(2, 4))

            if req["status"] not in ("RESOLVED", "CLOSED"):
                bf = ctk.CTkFrame(card, fg_color="transparent")
                bf.pack(fill="x", padx=10, pady=(0, 6))
                ctk.CTkButton(bf, text="Start Work", width=80,
                               command=lambda _r=req: self._start_work(_r)).pack(side="left", padx=3)
                ctk.CTkButton(bf, text="Resolve", width=70,
                               command=lambda _r=req: self._resolve_popup(_r)).pack(side="left", padx=3)
                ctk.CTkButton(bf, text="Reschedule", width=80,
                               command=lambda _r=req: self._schedule_popup(_r)).pack(side="left", padx=3)

    # ── Resolutions tab ───────────────────────────────────────────────

    def setup_resolutions_tab(self):
        frame = self.tab_resolutions
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_resolutions_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Resolution History")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            resolutions = self.service.get_resolution_history()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load resolutions.").pack(pady=20)
            return

        if not resolutions:
            ctk.CTkLabel(sf, text="No resolved maintenance records.").pack(pady=20)
            return

        headers = ["Unit", "Tenant", "Issue", "Resolution", "Hours", "Cost", "Date"]
        widths = [70, 110, 140, 170, 55, 75, 95]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i], anchor="w").pack(side="left", padx=3)

        for r in resolutions:
            rf = ctk.CTkFrame(sf, fg_color=("gray85", "gray17"))
            rf.pack(fill="x", pady=2, padx=5)
            # Add some inner padding/grid to make it look like a card row
            inner = ctk.CTkFrame(rf, fg_color="transparent")
            inner.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(inner, text=r["unit_code"], width=widths[0],
                         anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(inner, text=r["tenant_name"], width=widths[1],
                         anchor="w").pack(side="left", padx=3)
            desc = r["description"][:28] + "…" if len(r["description"]) > 28 else r["description"]
            ctk.CTkLabel(inner, text=desc, width=widths[2],
                         anchor="w").pack(side="left", padx=3)
            res_det = r["resolution_details"][:35] + "…" if len(r["resolution_details"]) > 35 else r["resolution_details"]
            ctk.CTkLabel(inner, text=res_det, width=widths[3],
                         anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(inner, text=f"{float(r['time_taken_hours']):.1f}h",
                         width=widths[4], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(inner, text=f"£{float(r['cost']):.2f}",
                         width=widths[5], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(inner, text=_uk_date(r["resolved_at"]),
                         width=widths[6], anchor="w").pack(side="left", padx=3)

    # ── Shared request list renderer ──────────────────────────────────

    def _render_request_list(self, parent, requests, show_actions=True):
        headers = ["Tenant", "Unit", "Priority", "Status", "Assigned To", "Date", "Actions"]
        widths = [120, 70, 70, 90, 110, 90, 200]
        hf = ctk.CTkFrame(parent)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i], anchor="w").pack(side="left", padx=3)

        for req in requests:
            # Card style
            rf = ctk.CTkFrame(parent, corner_radius=6, fg_color=("gray85", "gray17"))
            rf.pack(fill="x", pady=4, padx=5)
            
            # Using grid inside the card for better alignment if needed, 
            # but sticking to pack(side=left) to match headers structure for now
            # Layout: [Tenant | Unit | Priority | Status | Assigned | Date | Actions]
            
            # Inner container to hold the row content with padding
            inner = ctk.CTkFrame(rf, fg_color="transparent")
            inner.pack(fill="x", padx=5, pady=8)

            ctk.CTkLabel(inner, text=req["tenant_name"], width=widths[0], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(inner, text=req["unit_code"], width=widths[1], anchor="w").pack(side="left", padx=3)

            p_text = _humanise(req["priority"])
            p_colour = C.get(req["priority"], _GREY)
            ctk.CTkLabel(inner, text=p_text, width=widths[2], anchor="w",
                         text_color=p_colour, font=("Arial", 12, "bold")).pack(side="left", padx=3)

            s_text = _humanise(req["status"])
            s_colour = C.get(req["status"], _GREY)
            ctk.CTkLabel(inner, text=s_text, width=widths[3], anchor="w",
                         text_color=s_colour, font=("Arial", 12, "bold")).pack(side="left", padx=3)

            assigned = req["assigned_to"] or "Unassigned"
            ctk.CTkLabel(inner, text=assigned, width=widths[4], anchor="w").pack(side="left", padx=3)
            
            date_str = _uk_date(req["date_created"])
            ctk.CTkLabel(inner, text=date_str, width=widths[5], anchor="w").pack(side="left", padx=3)

            # Actions area
            action_frame = ctk.CTkFrame(inner, fg_color="transparent")
            action_frame.pack(side="left", padx=3, fill="both")
            
            if show_actions and req["status"] not in ("RESOLVED", "CLOSED"):
                if req["status"] == "REPORTED":
                    ctk.CTkButton(action_frame, text="Assign", width=55,
                                   command=lambda _r=req: self._assign_popup(_r)).pack(side="left", padx=2)
                if req["status"] in ("TRIAGED", "REPORTED"):
                    ctk.CTkButton(action_frame, text="Schedule", width=60,
                                   command=lambda _r=req: self._schedule_popup(_r)).pack(side="left", padx=2)
                if req["status"] in ("SCHEDULED", "TRIAGED"):
                    ctk.CTkButton(action_frame, text="Start", width=50,
                                   command=lambda _r=req: self._start_work(_r)).pack(side="left", padx=2)
                if req["status"] in ("IN_PROGRESS", "SCHEDULED", "TRIAGED"):
                    ctk.CTkButton(action_frame, text="Resolve", width=55,
                                   command=lambda _r=req: self._resolve_popup(_r)).pack(side="left", padx=2)
            elif req["status"] in ("RESOLVED", "CLOSED"):
                ctk.CTkLabel(action_frame, text="✓ Completed",
                             text_color="#2ecc71", anchor="w").pack(side="left", padx=3)

    # ── Action popups ─────────────────────────────────────────────────

    def _assign_popup(self, req):
        popup = ctk.CTkToplevel(self)
        popup.title("Assign Maintenance Staff")
        popup.geometry("400x200")
        popup.transient(self)
        popup.grab_set()

        staff = self.service.get_maintenance_staff()
        staff_map = {s["full_name"]: s["user_id"] for s in staff}
        if not staff_map:
            ctk.CTkLabel(popup, text="No maintenance staff available.").pack(pady=20)
            return

        ctk.CTkLabel(popup, text=f"Request #{req['request_id']}: {req['description'][:60]}",
                     font=("Arial", 12, "bold")).pack(pady=10, padx=10)

        staff_var = ctk.StringVar(value=list(staff_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=staff_var,
                           values=list(staff_map.keys())).pack(pady=5)

        def save():
            try:
                self.service.assign_request(req["request_id"],
                                            staff_map[staff_var.get()])
                messagebox.showinfo("Success", "Staff assigned.", parent=popup)
                popup.destroy()
                self._refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Assign", command=save).pack(pady=10)

    def _schedule_popup(self, req):
        popup = ctk.CTkToplevel(self)
        popup.title("Schedule Maintenance")
        popup.geometry("400x220")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Request #{req['request_id']}: {req['description'][:60]}",
                     font=("Arial", 12, "bold")).pack(pady=10, padx=10)

        ctk.CTkLabel(popup, text="Schedule Date & Time (YYYY-MM-DD HH:MM)",
                     font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5, 2))
        sched_entry = ctk.CTkEntry(popup, width=360)
        sched_entry.insert(0, str(date.today() + timedelta(days=1)) + " 09:00")
        sched_entry.pack(padx=20)

        def save():
            try:
                self.service.schedule_request(req["request_id"],
                                              sched_entry.get().strip())
                messagebox.showinfo("Success", "Maintenance scheduled.", parent=popup)
                popup.destroy()
                self._refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Schedule", command=save).pack(pady=15)

    def _start_work(self, req):
        try:
            self.service.start_work(req["request_id"])
            messagebox.showinfo("Success", "Request marked as In Progress.")
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _resolve_popup(self, req):
        popup = ctk.CTkToplevel(self)
        popup.title("Resolve Maintenance Request")
        popup.geometry("460x380")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Request #{req['request_id']}: {req['description'][:80]}",
                     font=("Arial", 12, "bold")).pack(pady=10, padx=10)

        ctk.CTkLabel(popup, text="Resolution Details",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 2))
        details_entry = ctk.CTkTextbox(popup, width=400, height=80)
        details_entry.pack(padx=20)

        ctk.CTkLabel(popup, text="Time Taken (hours)",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
        hours_entry = ctk.CTkEntry(popup, width=400)
        hours_entry.pack(padx=20)

        ctk.CTkLabel(popup, text="Cost (£)",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
        cost_entry = ctk.CTkEntry(popup, width=400)
        cost_entry.pack(padx=20)

        def save():
            details = details_entry.get("1.0", "end-1c").strip()
            if not details:
                messagebox.showwarning("Validation",
                                       "Resolution details required.", parent=popup)
                return
            try:
                hours = float(hours_entry.get() or 0)
                cost = float(cost_entry.get() or 0)
            except ValueError:
                messagebox.showwarning("Validation",
                                       "Hours and cost must be numbers.", parent=popup)
                return
            try:
                self.service.resolve_request(req["request_id"], details, hours, cost)
                messagebox.showinfo("Success", "Request resolved.", parent=popup)
                popup.destroy()
                self._refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Resolve", command=save).pack(pady=15)

    # ── Refresh helper ────────────────────────────────────────────────

    def _refresh_all(self):
        self.setup_overview_tab()
        self.setup_my_requests_tab()
        self.setup_all_requests_tab()
        self.setup_schedule_tab()
        self.setup_resolutions_tab()