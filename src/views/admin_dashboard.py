import customtkinter as ctk
from models.user import User
from services.admin_service import AdminService
from typing import TYPE_CHECKING
from tkinter import messagebox
from datetime import date, timedelta

if TYPE_CHECKING:
    from views.gui import App

# ── Status colour + human-readable maps ───────────────────────────

COMPLAINT_STATUS_COLOURS = {
    "OPEN":        "#3498db",
    "IN_PROGRESS": "#f1c40f",
    "RESOLVED":    "#2ecc71",
    "CLOSED":      "#e74c3c",
}

MAINTENANCE_STATUS_COLOURS = {
    "REPORTED":    "#3498db",
    "TRIAGED":     "#9b59b6",
    "SCHEDULED":   "#f39c12",
    "IN_PROGRESS": "#f1c40f",
    "RESOLVED":    "#2ecc71",
    "CLOSED":      "#e74c3c",
}

PRIORITY_COLOURS = {
    "LOW":    "#2ecc71",
    "MEDIUM": "#f39c12",
    "HIGH":   "#e67e22",
    "URGENT": "#e74c3c",
}

_DISPLAY_OVERRIDES = {
    "TRIAGED": "Assigned",
    "FRONT_DESK": "Front Desk",
    "FINANCE_MANAGER": "Finance Manager",
    "MAINTENANCE_STAFF": "Maintenance Staff",
    "ADMINISTRATOR": "Administrator",
    "MANAGER": "Manager",
}

def _humanise(text: str) -> str:
    if text in _DISPLAY_OVERRIDES:
        return _DISPLAY_OVERRIDES[text]
    return text.replace("_", " ").title()

def _uk_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        value = date.fromisoformat(value[:10])
    return value.strftime("%d/%m/%Y")


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.service = AdminService(user.user_id, user.location_id)

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        label = ctk.CTkLabel(
            self.header_frame,
            text=f"Admin Panel — {user.full_name}",
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
        self.tab_users = self.tab_view.add("Users")
        self.tab_tenants = self.tab_view.add("Tenants")
        self.tab_apartments = self.tab_view.add("Apartments")
        self.tab_leases = self.tab_view.add("Leases")
        self.tab_billing = self.tab_view.add("Billing")
        self.tab_maintenance = self.tab_view.add("Maintenance")
        self.tab_complaints = self.tab_view.add("Complaints")
        self.tab_reports = self.tab_view.add("Reports")

        self.setup_overview_tab()
        self.setup_users_tab()
        self.setup_tenants_tab()
        self.setup_apartments_tab()
        self.setup_leases_tab()
        self.setup_billing_tab()
        self.setup_maintenance_tab()
        self.setup_complaints_tab()
        self.setup_reports_tab()

    # ── helpers ────────────────────────────────────────────────────────

    def _clear(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _make_table(self, parent, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [140] * len(headers)
        hf = ctk.CTkFrame(parent)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=col_widths[i]).pack(side="left", padx=4)
        for row in rows:
            rf = ctk.CTkFrame(parent)
            rf.pack(fill="x", pady=1)
            for i, val in enumerate(row):
                ctk.CTkLabel(rf, text=str(val) if val is not None else "—",
                             width=col_widths[i], anchor="w").pack(side="left", padx=4)
        return hf

    # ── Overview ──────────────────────────────────────────────────────

    def setup_overview_tab(self):
        frame = self.tab_overview
        self._clear(frame)

        ctk.CTkLabel(frame, text="Dashboard Overview",
                     font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        try:
            stats = self.service.get_overview_stats()
        except Exception:
            ctk.CTkLabel(frame, text="Unable to load stats.").pack(pady=20)
            return

        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=10)

        items = [
            ("Total Apartments", stats["total_apartments"]),
            ("Occupied", stats["occupied"]),
            ("Vacant", stats["vacant"]),
            ("Under Maintenance", stats["maintenance_apt"]),
            ("Active Leases", stats["active_leases"]),
            ("Open Maintenance", stats["open_maintenance"]),
            ("Unpaid Invoices", stats["unpaid_invoices_count"]),
            ("Pending £", f"£{stats['unpaid_invoices_total']:.2f}"),
            ("Open Complaints", stats["open_complaints"]),
        ]
        for idx, (title, value) in enumerate(items):
            card = ctk.CTkFrame(cards_frame)
            card.grid(row=idx // 3, column=idx % 3, padx=8, pady=8, sticky="nsew")
            cards_frame.grid_columnconfigure(idx % 3, weight=1)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=str(value), font=("Arial", 22, "bold")).pack(pady=(0, 10))

        # Expiring leases alert
        try:
            expiring = self.service.get_expiring_leases(30)
        except Exception:
            expiring = []
        if expiring:
            alert = ctk.CTkFrame(frame, fg_color="#c0392b")
            alert.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(alert,
                         text=f"⚠  {len(expiring)} lease(s) expiring within 30 days",
                         text_color="white", font=("Arial", 13, "bold")).pack(pady=6)

    # ── Users tab ─────────────────────────────────────────────────────

    def setup_users_tab(self):
        frame = self.tab_users
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Add Staff User",
                       command=self._add_staff_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_users_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="All Users at Your Location")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            users = self.service.get_all_users()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load users.").pack(pady=20)
            return

        if not users:
            ctk.CTkLabel(sf, text="No users found.").pack(pady=20)
            return

        headers = ["Name", "Email", "Role", "Active", "Actions"]
        widths = [160, 200, 130, 60, 220]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=4)

        for u in users:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            raw_role = u["role"] or ("Tenant" if u["tenant_id"] else "—")
            role = _humanise(raw_role) if raw_role not in ("Tenant", "—") else raw_role
            active = "Yes" if u["is_active"] else "No"
            ctk.CTkLabel(rf, text=u["full_name"], width=widths[0], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=u["email"], width=widths[1], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=role, width=widths[2], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=active, width=widths[3], anchor="w").pack(side="left", padx=4)

            btn_frame = ctk.CTkFrame(rf, fg_color="transparent")
            btn_frame.pack(side="left", padx=4)
            uid = u["user_id"]
            ctk.CTkButton(btn_frame, text="Edit", width=60,
                           command=lambda _u=u: self._edit_user_popup(_u)).pack(side="left", padx=2)
            if u["is_active"]:
                ctk.CTkButton(btn_frame, text="Deactivate", width=80,
                               command=lambda _id=uid: self._toggle_user(_id, False)).pack(side="left", padx=2)
            else:
                ctk.CTkButton(btn_frame, text="Activate", width=80,
                               command=lambda _id=uid: self._toggle_user(_id, True)).pack(side="left", padx=2)

    def _toggle_user(self, user_id, active):
        try:
            self.service.toggle_user_active(user_id, active)
            self.setup_users_tab()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add_staff_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Staff User")
        popup.geometry("420x480")
        popup.transient(self)
        popup.grab_set()

        fields = {}
        for label_text, key in [("Full Name", "full_name"), ("Email", "email"),
                                 ("Phone", "phone"), ("Password", "password")]:
            ctk.CTkLabel(popup, text=label_text, font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
            entry = ctk.CTkEntry(popup, width=360,
                                  show="*" if key == "password" else "")
            entry.pack(padx=20)
            fields[key] = entry

        ctk.CTkLabel(popup, text="Role", font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
        role_var = ctk.StringVar(value="FRONT_DESK")
        ctk.CTkOptionMenu(popup, variable=role_var,
                           values=["FRONT_DESK", "FINANCE_MANAGER", "MAINTENANCE_STAFF",
                                   "ADMINISTRATOR", "MANAGER"]).pack(padx=20)

        def save():
            name = fields["full_name"].get().strip()
            email = fields["email"].get().strip()
            phone = fields["phone"].get().strip()
            pw = fields["password"].get()
            if not name or not email or not pw:
                messagebox.showwarning("Validation", "Name, email and password are required.", parent=popup)
                return
            try:
                self.service.create_staff_user(name, email, pw, phone, role_var.get())
                messagebox.showinfo("Success", "Staff user created.", parent=popup)
                popup.destroy()
                self.setup_users_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Create", command=save).pack(pady=20)

    def _edit_user_popup(self, user_data):
        popup = ctk.CTkToplevel(self)
        popup.title("Edit User")
        popup.geometry("420x350")
        popup.transient(self)
        popup.grab_set()

        fields = {}
        for label_text, key, default in [
            ("Full Name", "full_name", user_data["full_name"]),
            ("Email", "email", user_data["email"]),
            ("Phone", "phone", user_data.get("phone") or ""),
        ]:
            ctk.CTkLabel(popup, text=label_text, font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
            entry = ctk.CTkEntry(popup, width=360)
            entry.insert(0, default)
            entry.pack(padx=20)
            fields[key] = entry

        def save():
            try:
                self.service.update_user(
                    user_data["user_id"],
                    fields["full_name"].get().strip(),
                    fields["email"].get().strip(),
                    fields["phone"].get().strip(),
                )
                messagebox.showinfo("Success", "User updated.", parent=popup)
                popup.destroy()
                self.setup_users_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Save", command=save).pack(pady=20)

    # ── Tenants tab ───────────────────────────────────────────────────

    def setup_tenants_tab(self):
        frame = self.tab_tenants
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Register Tenant",
                       command=self._register_tenant_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_tenants_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Tenant Records")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            tenants = self.service.get_all_tenants()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load tenants.").pack(pady=20)
            return

        if not tenants:
            ctk.CTkLabel(sf, text="No tenants found.").pack(pady=20)
            return

        headers = ["Name", "Email", "NI Number", "Occupation", "Active", "Actions"]
        widths = [140, 180, 110, 120, 50, 260]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=4)

        for t in tenants:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            ctk.CTkLabel(rf, text=t["full_name"], width=widths[0], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=t["email"], width=widths[1], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=t["ni_number"], width=widths[2], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=t.get("occupation") or "—", width=widths[3], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text="Yes" if t["is_active"] else "No", width=widths[4], anchor="w").pack(side="left", padx=4)

            bf = ctk.CTkFrame(rf, fg_color="transparent")
            bf.pack(side="left", padx=4)
            ctk.CTkButton(bf, text="Edit", width=55,
                           command=lambda _t=t: self._edit_tenant_popup(_t)).pack(side="left", padx=2)
            ctk.CTkButton(bf, text="Leases", width=55,
                           command=lambda _t=t: self._view_tenant_leases(_t)).pack(side="left", padx=2)
            ctk.CTkButton(bf, text="Payments", width=65,
                           command=lambda _t=t: self._view_tenant_payments(_t)).pack(side="left", padx=2)
            ctk.CTkButton(bf, text="Complaints", width=75,
                           command=lambda _t=t: self._view_tenant_complaints(_t)).pack(side="left", padx=2)

    def _register_tenant_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Register New Tenant")
        popup.geometry("450x620")
        popup.transient(self)
        popup.grab_set()

        fields = {}
        for lbl, key in [("Full Name*", "full_name"), ("Email*", "email"),
                          ("Phone", "phone"), ("Password*", "password"),
                          ("NI Number*", "ni_number"), ("Occupation", "occupation"),
                          ("References", "references"), ("Requirements", "requirements")]:
            ctk.CTkLabel(popup, text=lbl, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(6, 1))
            entry = ctk.CTkEntry(popup, width=400,
                                  show="*" if key == "password" else "")
            entry.pack(padx=20)
            fields[key] = entry

        def save():
            name = fields["full_name"].get().strip()
            email = fields["email"].get().strip()
            pw = fields["password"].get()
            ni = fields["ni_number"].get().strip()
            if not all([name, email, pw, ni]):
                messagebox.showwarning("Validation", "Fields marked * are required.", parent=popup)
                return
            try:
                self.service.register_tenant(
                    name, email, pw,
                    fields["phone"].get().strip(),
                    ni,
                    fields["occupation"].get().strip(),
                    fields["references"].get().strip(),
                    fields["requirements"].get().strip(),
                )
                messagebox.showinfo("Success", "Tenant registered.", parent=popup)
                popup.destroy()
                self.setup_tenants_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Register", command=save).pack(pady=15)

    def _edit_tenant_popup(self, tenant):
        popup = ctk.CTkToplevel(self)
        popup.title("Edit Tenant")
        popup.geometry("450x480")
        popup.transient(self)
        popup.grab_set()

        fields = {}
        for lbl, key, val in [
            ("Full Name", "full_name", tenant["full_name"]),
            ("Email", "email", tenant["email"]),
            ("Phone", "phone", tenant.get("phone") or ""),
            ("Occupation", "occupation", tenant.get("occupation") or ""),
            ("References", "references", tenant.get("references_txt") or ""),
            ("Requirements", "requirements", tenant.get("requirements") or ""),
        ]:
            ctk.CTkLabel(popup, text=lbl, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(6, 1))
            entry = ctk.CTkEntry(popup, width=400)
            entry.insert(0, val)
            entry.pack(padx=20)
            fields[key] = entry

        def save():
            try:
                self.service.update_tenant(
                    tenant["tenant_id"],
                    fields["full_name"].get().strip(),
                    fields["email"].get().strip(),
                    fields["phone"].get().strip(),
                    fields["occupation"].get().strip(),
                    fields["references"].get().strip(),
                    fields["requirements"].get().strip(),
                )
                messagebox.showinfo("Success", "Tenant updated.", parent=popup)
                popup.destroy()
                self.setup_tenants_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Save", command=save).pack(pady=15)

    def _view_tenant_leases(self, tenant):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Leases — {tenant['full_name']}")
        popup.geometry("700x400")
        popup.transient(self)
        popup.grab_set()

        sf = ctk.CTkScrollableFrame(popup)
        sf.pack(fill="both", expand=True, padx=10, pady=10)

        leases = self.service.get_tenant_leases(tenant["tenant_id"])
        if not leases:
            ctk.CTkLabel(sf, text="No leases found.").pack(pady=20)
            return

        headers = ["Unit", "City", "Start", "End", "Rent", "Status"]
        widths = [80, 100, 100, 100, 80, 120]
        self._make_table(sf, headers,
                         [(l["unit_code"], l["city"], str(l["start_date"]),
                           str(l["end_date"]), f"£{l['monthly_rent']}",
                           l["status"]) for l in leases], widths)

    def _view_tenant_payments(self, tenant):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Payments — {tenant['full_name']}")
        popup.geometry("700x400")
        popup.transient(self)
        popup.grab_set()

        sf = ctk.CTkScrollableFrame(popup)
        sf.pack(fill="both", expand=True, padx=10, pady=10)

        payments = self.service.get_tenant_payments(tenant["tenant_id"])
        if not payments:
            ctk.CTkLabel(sf, text="No payments found.").pack(pady=20)
            return

        headers = ["Date", "Amount", "Method", "Due Date", "Inv Status"]
        widths = [130, 90, 110, 100, 90]
        self._make_table(sf, headers,
                         [(str(p["paid_at"]), f"£{p['amount_paid']}",
                           p["method"], str(p["due_date"]),
                           p["inv_status"]) for p in payments], widths)

    def _view_tenant_complaints(self, tenant):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Complaints — {tenant['full_name']}")
        popup.geometry("700x400")
        popup.transient(self)
        popup.grab_set()

        sf = ctk.CTkScrollableFrame(popup)
        sf.pack(fill="both", expand=True, padx=10, pady=10)

        complaints = self.service.get_tenant_complaints(tenant["tenant_id"])
        if not complaints:
            ctk.CTkLabel(sf, text="No complaints found.").pack(pady=20)
            return

        headers = ["Date", "Description", "Status"]
        widths = [130, 350, 100]
        self._make_table(sf, headers,
                         [(str(c["date_created"]), c["description"],
                           c["status"]) for c in complaints], widths)

    # ── Apartments tab ────────────────────────────────────────────────

    def setup_apartments_tab(self):
        frame = self.tab_apartments
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Add Apartment",
                       command=self._add_apartment_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_apartments_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Apartments")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            apts = self.service.get_all_apartments()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load apartments.").pack(pady=20)
            return

        if not apts:
            ctk.CTkLabel(sf, text="No apartments found.").pack(pady=20)
            return

        headers = ["Unit", "Type", "Rooms", "Rent", "Status", "Actions"]
        widths = [100, 120, 60, 100, 110, 100]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=4)

        for a in apts:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            ctk.CTkLabel(rf, text=a["unit_code"], width=widths[0], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=a["apt_type"], width=widths[1], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=str(a["rooms"]), width=widths[2], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=f"£{a['monthly_rent']}", width=widths[3], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=a["status"], width=widths[4], anchor="w").pack(side="left", padx=4)
            ctk.CTkButton(rf, text="Edit", width=60,
                           command=lambda _a=a: self._edit_apartment_popup(_a)).pack(side="left", padx=4)

    def _add_apartment_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Apartment")
        popup.geometry("420x400")
        popup.transient(self)
        popup.grab_set()

        fields = {}
        for lbl, key in [("Unit Code", "unit_code"), ("Type (e.g. 2-Bed Flat)", "apt_type"),
                          ("Monthly Rent (£)", "monthly_rent"), ("Rooms", "rooms")]:
            ctk.CTkLabel(popup, text=lbl, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
            entry = ctk.CTkEntry(popup, width=360)
            entry.pack(padx=20)
            fields[key] = entry

        def save():
            try:
                rent = float(fields["monthly_rent"].get())
                rooms = int(fields["rooms"].get())
            except ValueError:
                messagebox.showwarning("Validation", "Rent and rooms must be numbers.", parent=popup)
                return
            unit = fields["unit_code"].get().strip()
            atype = fields["apt_type"].get().strip()
            if not unit or not atype:
                messagebox.showwarning("Validation", "All fields are required.", parent=popup)
                return
            try:
                self.service.add_apartment(unit, atype, rent, rooms)
                messagebox.showinfo("Success", "Apartment added.", parent=popup)
                popup.destroy()
                self.setup_apartments_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Add", command=save).pack(pady=20)

    def _edit_apartment_popup(self, apt):
        popup = ctk.CTkToplevel(self)
        popup.title("Edit Apartment")
        popup.geometry("420x450")
        popup.transient(self)
        popup.grab_set()

        fields = {}
        for lbl, key, val in [
            ("Unit Code", "unit_code", apt["unit_code"]),
            ("Type", "apt_type", apt["apt_type"]),
            ("Monthly Rent (£)", "monthly_rent", str(apt["monthly_rent"])),
            ("Rooms", "rooms", str(apt["rooms"])),
        ]:
            ctk.CTkLabel(popup, text=lbl, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
            entry = ctk.CTkEntry(popup, width=360)
            entry.insert(0, val)
            entry.pack(padx=20)
            fields[key] = entry

        ctk.CTkLabel(popup, text="Status", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
        status_var = ctk.StringVar(value=apt["status"])
        ctk.CTkOptionMenu(popup, variable=status_var,
                           values=["VACANT", "OCCUPIED", "MAINTENANCE"]).pack(padx=20)

        def save():
            try:
                rent = float(fields["monthly_rent"].get())
                rooms = int(fields["rooms"].get())
            except ValueError:
                messagebox.showwarning("Validation", "Rent and rooms must be numbers.", parent=popup)
                return
            try:
                self.service.update_apartment(
                    apt["apartment_id"],
                    fields["unit_code"].get().strip(),
                    fields["apt_type"].get().strip(),
                    rent, rooms, status_var.get(),
                )
                messagebox.showinfo("Success", "Apartment updated.", parent=popup)
                popup.destroy()
                self.setup_apartments_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Save", command=save).pack(pady=20)

    # ── Leases tab ────────────────────────────────────────────────────

    def setup_leases_tab(self):
        frame = self.tab_leases
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Create Lease",
                       command=self._create_lease_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_leases_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Lease Agreements")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            leases = self.service.get_all_leases()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load leases.").pack(pady=20)
            return

        if not leases:
            ctk.CTkLabel(sf, text="No leases found.").pack(pady=20)
            return

        headers = ["Tenant", "Unit", "Start", "End", "Rent", "Status", "Actions"]
        widths = [130, 80, 95, 95, 80, 130, 160]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=3)

        for l in leases:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            status_text = l["status"]
            if l["early_leave_notice_date"]:
                status_text += " (Early)"
            ctk.CTkLabel(rf, text=l["tenant_name"], width=widths[0], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=l["unit_code"], width=widths[1], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=str(l["start_date"]), width=widths[2], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=str(l["end_date"]), width=widths[3], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=f"£{l['monthly_rent']}", width=widths[4], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=status_text, width=widths[5], anchor="w").pack(side="left", padx=3)

            bf = ctk.CTkFrame(rf, fg_color="transparent")
            bf.pack(side="left", padx=3)
            if l["status"] == "ACTIVE":
                ctk.CTkButton(bf, text="End", width=50,
                               command=lambda _l=l: self._end_lease(_l)).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="Early Term.", width=80,
                               command=lambda _l=l: self._early_termination_popup(_l)).pack(side="left", padx=2)

    def _create_lease_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Create Lease")
        popup.geometry("460x500")
        popup.transient(self)
        popup.grab_set()

        # Tenant selection
        tenants = self.service.get_all_tenants()
        tenant_map = {f"{t['full_name']} ({t['ni_number']})": t["tenant_id"] for t in tenants}
        if not tenant_map:
            ctk.CTkLabel(popup, text="No tenants available.").pack(pady=20)
            return

        ctk.CTkLabel(popup, text="Tenant", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        tenant_var = ctk.StringVar(value=list(tenant_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=tenant_var,
                           values=list(tenant_map.keys())).pack(padx=20, anchor="w")

        # Apartment selection
        apts = self.service.get_vacant_apartments()
        apt_map = {f"{a['unit_code']} — {a['apt_type']} (£{a['monthly_rent']})": a for a in apts}
        if not apt_map:
            ctk.CTkLabel(popup, text="No vacant apartments.").pack(pady=20)
            return

        ctk.CTkLabel(popup, text="Apartment", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        apt_var = ctk.StringVar(value=list(apt_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=apt_var,
                           values=list(apt_map.keys())).pack(padx=20, anchor="w")

        fields = {}
        today = date.today()
        for lbl, key, default in [
            ("Start Date (YYYY-MM-DD)", "start", str(today)),
            ("End Date (YYYY-MM-DD)", "end", str(today + timedelta(days=365))),
            ("Monthly Rent (£)", "rent", ""),
        ]:
            ctk.CTkLabel(popup, text=lbl, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
            entry = ctk.CTkEntry(popup, width=400)
            entry.insert(0, default)
            entry.pack(padx=20)
            fields[key] = entry

        # Auto-fill rent from apartment selection
        def on_apt_change(choice):
            a = apt_map.get(choice)
            if a:
                fields["rent"].delete(0, "end")
                fields["rent"].insert(0, str(a["monthly_rent"]))
        apt_var.trace_add("write", lambda *_: on_apt_change(apt_var.get()))
        on_apt_change(apt_var.get())

        def save():
            tid = tenant_map[tenant_var.get()]
            apt = apt_map[apt_var.get()]
            try:
                rent = float(fields["rent"].get())
            except ValueError:
                messagebox.showwarning("Validation", "Rent must be a number.", parent=popup)
                return
            try:
                self.service.create_lease(tid, apt["apartment_id"],
                                          fields["start"].get().strip(),
                                          fields["end"].get().strip(), rent)
                messagebox.showinfo("Success", "Lease created.", parent=popup)
                popup.destroy()
                self.setup_leases_tab()
                self.setup_apartments_tab()
                self.setup_overview_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Create Lease", command=save).pack(pady=20)

    def _end_lease(self, lease_data):
        if not messagebox.askyesno("Confirm", f"End lease #{lease_data['lease_id']} for {lease_data['tenant_name']}?"):
            return
        try:
            self.service.end_lease(lease_data["lease_id"])
            self.setup_leases_tab()
            self.setup_apartments_tab()
            self.setup_overview_tab()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _early_termination_popup(self, lease_data):
        popup = ctk.CTkToplevel(self)
        popup.title("Early Termination")
        popup.geometry("440x350")
        popup.transient(self)
        popup.grab_set()

        rent = float(lease_data["monthly_rent"])
        penalty = round(rent * 0.05, 2)

        ctk.CTkLabel(popup, text=f"Lease #{lease_data['lease_id']} — {lease_data['tenant_name']}",
                     font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(popup, text=f"Monthly rent: £{rent:.2f}").pack()
        ctk.CTkLabel(popup, text=f"Early termination penalty (5%): £{penalty:.2f}",
                     font=("Arial", 13, "bold")).pack(pady=5)

        today = date.today()
        notice_date = str(today)
        requested_end = str(today + timedelta(days=30))

        ctk.CTkLabel(popup, text="Notice Date (YYYY-MM-DD)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        notice_entry = ctk.CTkEntry(popup, width=380)
        notice_entry.insert(0, notice_date)
        notice_entry.pack(padx=20)

        ctk.CTkLabel(popup, text="Requested End (min 1 month)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        end_entry = ctk.CTkEntry(popup, width=380)
        end_entry.insert(0, requested_end)
        end_entry.pack(padx=20)

        def save():
            try:
                self.service.process_early_termination(
                    lease_data["lease_id"],
                    notice_entry.get().strip(),
                    end_entry.get().strip(),
                    penalty,
                )
                messagebox.showinfo("Success", "Early termination processed.", parent=popup)
                popup.destroy()
                self.setup_leases_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Process Termination", command=save).pack(pady=15)

    # ── Billing tab ───────────────────────────────────────────────────

    def setup_billing_tab(self):
        frame = self.tab_billing
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Create Invoice",
                       command=self._create_invoice_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Record Payment",
                       command=self._record_payment_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="View Late Invoices",
                       command=self._view_late_invoices).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_billing_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="All Invoices")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            invoices = self.service.get_all_invoices()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load invoices.").pack(pady=20)
            return

        if not invoices:
            ctk.CTkLabel(sf, text="No invoices found.").pack(pady=20)
            return

        headers = ["ID", "Tenant", "Unit", "Due Date", "Amount", "Status"]
        widths = [50, 140, 80, 100, 90, 80]
        self._make_table(sf, headers,
                         [(inv["invoice_id"], inv["tenant_name"], inv["unit_code"],
                           str(inv["due_date"]), f"£{inv['amount']}",
                           inv["status"]) for inv in invoices], widths)

    def _create_invoice_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Create Invoice")
        popup.geometry("460x400")
        popup.transient(self)
        popup.grab_set()

        leases = self.service.get_all_leases()
        active = [l for l in leases if l["status"] == "ACTIVE"]
        lease_map = {f"{l['tenant_name']} — {l['unit_code']} (£{l['monthly_rent']})": l for l in active}
        if not lease_map:
            ctk.CTkLabel(popup, text="No active leases to invoice.").pack(pady=20)
            return

        ctk.CTkLabel(popup, text="Lease", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        lease_var = ctk.StringVar(value=list(lease_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=lease_var,
                           values=list(lease_map.keys())).pack(padx=20, anchor="w")

        ctk.CTkLabel(popup, text="Due Date (YYYY-MM-DD)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        due_entry = ctk.CTkEntry(popup, width=400)
        due_entry.insert(0, str(date.today() + timedelta(days=30)))
        due_entry.pack(padx=20)

        ctk.CTkLabel(popup, text="Amount (£)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        amount_entry = ctk.CTkEntry(popup, width=400)
        amount_entry.pack(padx=20)

        def on_lease_change(choice):
            l = lease_map.get(choice)
            if l:
                amount_entry.delete(0, "end")
                amount_entry.insert(0, str(l["monthly_rent"]))
        lease_var.trace_add("write", lambda *_: on_lease_change(lease_var.get()))
        on_lease_change(lease_var.get())

        def save():
            l = lease_map[lease_var.get()]
            try:
                amount = float(amount_entry.get())
            except ValueError:
                messagebox.showwarning("Validation", "Amount must be a number.", parent=popup)
                return
            try:
                self.service.create_invoice(l["tenant_id"], l["lease_id"],
                                            due_entry.get().strip(), amount)
                messagebox.showinfo("Success", "Invoice created.", parent=popup)
                popup.destroy()
                self.setup_billing_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Create Invoice", command=save).pack(pady=20)

    def _record_payment_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Record Payment")
        popup.geometry("460x400")
        popup.transient(self)
        popup.grab_set()

        invoices = [inv for inv in self.service.get_all_invoices()
                    if inv["status"] in ("UNPAID", "LATE")]
        inv_map = {f"#{inv['invoice_id']} — {inv['tenant_name']} £{inv['amount']} (Due: {inv['due_date']})": inv
                   for inv in invoices}
        if not inv_map:
            ctk.CTkLabel(popup, text="No unpaid invoices.").pack(pady=20)
            return

        ctk.CTkLabel(popup, text="Invoice", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        inv_var = ctk.StringVar(value=list(inv_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=inv_var,
                           values=list(inv_map.keys())).pack(padx=20, anchor="w")

        ctk.CTkLabel(popup, text="Amount (£)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        amt_entry = ctk.CTkEntry(popup, width=400)
        amt_entry.pack(padx=20)

        def on_inv_change(choice):
            inv = inv_map.get(choice)
            if inv:
                amt_entry.delete(0, "end")
                amt_entry.insert(0, str(inv["amount"]))
        inv_var.trace_add("write", lambda *_: on_inv_change(inv_var.get()))
        on_inv_change(inv_var.get())

        ctk.CTkLabel(popup, text="Method", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        method_var = ctk.StringVar(value="BANK_TRANSFER")
        ctk.CTkOptionMenu(popup, variable=method_var,
                           values=["CASH", "CARD", "BANK_TRANSFER", "CHEQUE", "OTHER"]).pack(padx=20, anchor="w")

        def save():
            inv = inv_map[inv_var.get()]
            try:
                amount = float(amt_entry.get())
            except ValueError:
                messagebox.showwarning("Validation", "Amount must be a number.", parent=popup)
                return
            try:
                self.service.record_payment(inv["invoice_id"], amount, method_var.get())
                messagebox.showinfo("Success", "Payment recorded.", parent=popup)
                popup.destroy()
                self.setup_billing_tab()
                self.setup_overview_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Record Payment", command=save).pack(pady=20)

    def _view_late_invoices(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Late / Overdue Invoices")
        popup.geometry("700x400")
        popup.transient(self)
        popup.grab_set()

        sf = ctk.CTkScrollableFrame(popup)
        sf.pack(fill="both", expand=True, padx=10, pady=10)

        late = self.service.get_late_invoices()
        if not late:
            ctk.CTkLabel(sf, text="No late invoices.").pack(pady=20)
            return

        headers = ["ID", "Tenant", "Unit", "Due Date", "Amount", "Notify"]
        widths = [50, 140, 80, 100, 90, 100]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=4)

        for inv in late:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            ctk.CTkLabel(rf, text=str(inv["invoice_id"]), width=widths[0], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=inv["tenant_name"], width=widths[1], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=inv["unit_code"], width=widths[2], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=str(inv["due_date"]), width=widths[3], anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=f"£{inv['amount']}", width=widths[4], anchor="w").pack(side="left", padx=4)
            # We need the tenant_id to send notification — fetch from invoices join
            ctk.CTkButton(rf, text="Send Alert", width=80,
                           command=lambda _inv=inv: self._send_late_alert(_inv, popup)).pack(side="left", padx=4)

    def _send_late_alert(self, inv_data, parent_popup):
        # Get tenant_id from invoice
        result = execute_read_for_alert(inv_data["invoice_id"])
        if result:
            tid = result[0]["tenant_id"]
            msg = f"Your invoice #{inv_data['invoice_id']} of £{inv_data['amount']} was due on {inv_data['due_date']}. Please settle immediately."
            self.service.send_late_notification(tid, msg)
            messagebox.showinfo("Sent", "Late payment notification sent.", parent=parent_popup)
        else:
            messagebox.showerror("Error", "Could not find tenant for this invoice.", parent=parent_popup)

    # ── Maintenance tab ───────────────────────────────────────────────

    def setup_maintenance_tab(self):
        frame = self.tab_maintenance
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_maintenance_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Maintenance Requests")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            requests = self.service.get_all_maintenance_requests()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load requests.").pack(pady=20)
            return

        if not requests:
            ctk.CTkLabel(sf, text="No maintenance requests found.").pack(pady=20)
            return

        headers = ["Tenant", "Unit", "Priority", "Status", "Assigned To", "Date", "Actions"]
        widths = [120, 70, 70, 90, 110, 90, 200]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=3)

        for req in requests:
            rf = ctk.CTkFrame(sf, height=36)
            rf.pack(fill="x", pady=1)
            rf.pack_propagate(False)
            ctk.CTkLabel(rf, text=req["tenant_name"], width=widths[0], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=req["unit_code"], width=widths[1], anchor="w").pack(side="left", padx=3)
            p_text = _humanise(req["priority"])
            p_colour = PRIORITY_COLOURS.get(req["priority"], "#cccccc")
            ctk.CTkLabel(rf, text=p_text, width=widths[2], anchor="w",
                         text_color=p_colour, font=("Arial", 12, "bold")).pack(side="left", padx=3)
            s_text = _humanise(req["status"])
            s_colour = MAINTENANCE_STATUS_COLOURS.get(req["status"], "#cccccc")
            ctk.CTkLabel(rf, text=s_text, width=widths[3], anchor="w",
                         text_color=s_colour, font=("Arial", 12, "bold")).pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=req["assigned_to"] or "Unassigned", width=widths[4], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=_uk_date(req["date_created"]), width=widths[5], anchor="w").pack(side="left", padx=3)

            if req["status"] not in ("RESOLVED", "CLOSED"):
                bf = ctk.CTkFrame(rf, fg_color="transparent")
                bf.pack(side="left", padx=3)
                ctk.CTkButton(bf, text="Assign", width=55,
                               command=lambda _r=req: self._assign_maintenance_popup(_r)).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="Schedule", width=60,
                               command=lambda _r=req: self._schedule_maintenance_popup(_r)).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="Resolve", width=55,
                               command=lambda _r=req: self._resolve_maintenance_popup(_r)).pack(side="left", padx=2)
            else:
                ctk.CTkLabel(rf, text="✓ Completed", width=widths[6],
                             text_color="#2ecc71", anchor="w").pack(side="left", padx=3)

    def _assign_maintenance_popup(self, req):
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
                self.service.assign_maintenance(req["request_id"], staff_map[staff_var.get()])
                messagebox.showinfo("Success", "Staff assigned.", parent=popup)
                popup.destroy()
                self.setup_maintenance_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Assign", command=save).pack(pady=10)

    def _schedule_maintenance_popup(self, req):
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
                self.service.schedule_maintenance(req["request_id"], sched_entry.get().strip())
                messagebox.showinfo("Success", "Maintenance scheduled.", parent=popup)
                popup.destroy()
                self.setup_maintenance_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Schedule", command=save).pack(pady=15)

    def _resolve_maintenance_popup(self, req):
        popup = ctk.CTkToplevel(self)
        popup.title("Resolve Maintenance Request")
        popup.geometry("460x380")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Request #{req['request_id']}: {req['description'][:80]}",
                     font=("Arial", 12, "bold")).pack(pady=10, padx=10)

        ctk.CTkLabel(popup, text="Resolution Details", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 2))
        details_entry = ctk.CTkTextbox(popup, width=400, height=80)
        details_entry.pack(padx=20)

        ctk.CTkLabel(popup, text="Time Taken (hours)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
        hours_entry = ctk.CTkEntry(popup, width=400)
        hours_entry.pack(padx=20)

        ctk.CTkLabel(popup, text="Cost (£)", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(8, 2))
        cost_entry = ctk.CTkEntry(popup, width=400)
        cost_entry.pack(padx=20)

        def save():
            details = details_entry.get("1.0", "end-1c").strip()
            if not details:
                messagebox.showwarning("Validation", "Resolution details required.", parent=popup)
                return
            try:
                hours = float(hours_entry.get() or 0)
                cost = float(cost_entry.get() or 0)
            except ValueError:
                messagebox.showwarning("Validation", "Hours and cost must be numbers.", parent=popup)
                return
            try:
                self.service.resolve_maintenance(req["request_id"], details, hours, cost)
                messagebox.showinfo("Success", "Request resolved.", parent=popup)
                popup.destroy()
                self.setup_maintenance_tab()
                self.setup_overview_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Resolve", command=save).pack(pady=15)

    # ── Complaints tab ────────────────────────────────────────────────

    def setup_complaints_tab(self):
        frame = self.tab_complaints
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_complaints_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Complaints")
        sf.pack(fill="both", expand=True, pady=5)

        try:
            complaints = self.service.get_all_complaints()
        except Exception:
            ctk.CTkLabel(sf, text="Unable to load complaints.").pack(pady=20)
            return

        if not complaints:
            ctk.CTkLabel(sf, text="No complaints found.").pack(pady=20)
            return

        headers = ["Tenant", "Unit", "Date", "Description", "Status", "Actions"]
        widths = [120, 70, 95, 220, 90, 140]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                         width=widths[i]).pack(side="left", padx=3)

        for c in complaints:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            ctk.CTkLabel(rf, text=c["tenant_name"], width=widths[0], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=c.get("unit_code") or "—", width=widths[1], anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(rf, text=_uk_date(c["date_created"]), width=widths[2], anchor="w").pack(side="left", padx=3)
            desc = c["description"][:40] + "…" if len(c["description"]) > 40 else c["description"]
            ctk.CTkLabel(rf, text=desc, width=widths[3], anchor="w").pack(side="left", padx=3)
            cs_text = _humanise(c["status"])
            cs_colour = COMPLAINT_STATUS_COLOURS.get(c["status"], "#cccccc")
            ctk.CTkLabel(rf, text=cs_text, width=widths[4], anchor="w",
                         text_color=cs_colour, font=("Arial", 12, "bold")).pack(side="left", padx=3)

            if c["status"] not in ("RESOLVED", "CLOSED"):
                bf = ctk.CTkFrame(rf, fg_color="transparent")
                bf.pack(side="left", padx=3)
                for status_opt, btn_text in [("IN_PROGRESS", "In Prog."), ("RESOLVED", "Resolve"), ("CLOSED", "Close")]:
                    if c["status"] != status_opt:
                        ctk.CTkButton(bf, text=btn_text, width=55,
                                       command=lambda _cid=c["complaint_id"], _s=status_opt:
                                       self._update_complaint(_cid, _s)).pack(side="left", padx=1)

    def _update_complaint(self, complaint_id, status):
        try:
            self.service.update_complaint_status(complaint_id, status)
            self.setup_complaints_tab()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Reports tab ───────────────────────────────────────────────────

    def setup_reports_tab(self):
        frame = self.tab_reports
        self._clear(frame)

        ctk.CTkLabel(frame, text="Reports", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Occupancy Report",
                       command=self._show_occupancy_report).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Financial Summary",
                       command=self._show_financial_summary).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Maintenance Costs",
                       command=self._show_maintenance_cost_report).pack(side="left", padx=5)

        self.report_output = ctk.CTkScrollableFrame(frame, label_text="Report Output")
        self.report_output.pack(fill="both", expand=True, padx=10, pady=5)

    def _show_occupancy_report(self):
        self._clear(self.report_output)

        data = self.service.get_occupancy_report()
        if not data:
            ctk.CTkLabel(self.report_output, text="No data.").pack(pady=20)
            return

        # Summary counts
        total = len(data)
        occupied = sum(1 for d in data if d["status"] == "OCCUPIED")
        vacant = sum(1 for d in data if d["status"] == "VACANT")
        maint = sum(1 for d in data if d["status"] == "MAINTENANCE")
        rate = (occupied / total * 100) if total > 0 else 0

        summary_frame = ctk.CTkFrame(self.report_output)
        summary_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(summary_frame, text=f"Occupancy Rate: {rate:.1f}%  |  "
                     f"Total: {total}  |  Occupied: {occupied}  |  "
                     f"Vacant: {vacant}  |  Maintenance: {maint}",
                     font=("Arial", 13, "bold")).pack(pady=8, padx=10)

        headers = ["Unit", "Type", "Rooms", "Rent", "Status", "City"]
        widths = [80, 120, 60, 90, 100, 120]
        self._make_table(self.report_output, headers,
                         [(d["unit_code"], d["apt_type"], d["rooms"],
                           f"£{d['monthly_rent']}", d["status"],
                           d["city"]) for d in data], widths)

    def _show_financial_summary(self):
        self._clear(self.report_output)

        data = self.service.get_financial_summary()

        summary_frame = ctk.CTkFrame(self.report_output)
        summary_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(summary_frame,
                     text=f"Total Collected: £{data['total_collected']:.2f}  |  "
                          f"Total Pending: £{data['total_pending']:.2f}",
                     font=("Arial", 14, "bold")).pack(pady=8, padx=10)

        if data["monthly_breakdown"]:
            ctk.CTkLabel(self.report_output, text="Monthly Breakdown",
                         font=("Arial", 13, "bold")).pack(anchor="w", padx=5, pady=(10, 5))
            headers = ["Month", "Amount Collected"]
            widths = [120, 150]
            self._make_table(self.report_output, headers,
                             [(m["month"], f"£{float(m['total']):.2f}")
                              for m in data["monthly_breakdown"]], widths)
        else:
            ctk.CTkLabel(self.report_output, text="No payment data yet.").pack(pady=10)

    def _show_maintenance_cost_report(self):
        self._clear(self.report_output)

        data = self.service.get_maintenance_cost_report()
        if not data:
            ctk.CTkLabel(self.report_output, text="No resolved maintenance data.").pack(pady=20)
            return

        total_cost = sum(float(d["cost"]) for d in data)
        total_hours = sum(float(d["time_taken_hours"]) for d in data)

        summary_frame = ctk.CTkFrame(self.report_output)
        summary_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(summary_frame,
                     text=f"Total Maintenance Cost: £{total_cost:.2f}  |  "
                          f"Total Hours: {total_hours:.1f}",
                     font=("Arial", 14, "bold")).pack(pady=8, padx=10)

        headers = ["Unit", "Issue", "Resolution", "Hours", "Cost", "Date"]
        widths = [70, 150, 170, 60, 80, 95]
        self._make_table(self.report_output, headers,
                         [(d["unit_code"],
                           d["description"][:30],
                           d["resolution_details"][:35],
                           str(d["time_taken_hours"]),
                           f"£{d['cost']}",
                           str(d["resolved_at"])[:10]) for d in data], widths)


# Helper for late payment alert (avoids circular import)
def execute_read_for_alert(invoice_id):
    from utils.db_utils import execute_read
    return execute_read(
        "SELECT tenant_id FROM invoices WHERE invoice_id = %s",
        (invoice_id,),
    )