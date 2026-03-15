import customtkinter as ctk
from models.user import User
from services.admin_service import AdminService
from services.maintenance_service import MaintenanceService
from typing import TYPE_CHECKING
from tkinter import messagebox
from datetime import datetime

if TYPE_CHECKING:
    from views.gui import App

# ── Colours ───────────────────────────────────────────────────────
C = {
    "OPEN":        "#3498db",
    "IN_PROGRESS": "#f1c40f",
    "RESOLVED":    "#2ecc71",
    "CLOSED":      "#e74c3c",
    "REPORTED":    "#3498db",
    "TRIAGED":     "#9b59b6",
    "SCHEDULED":   "#f39c12",
}

class FrontDeskDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        # AdminService has tenant registration & lease logic
        self.admin_service = AdminService(user.user_id, user.location_id)
        # MaintenanceService has request logging logic
        self.maint_service = MaintenanceService(user.user_id, user.location_id)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        label = ctk.CTkLabel(self.header_frame, text=f"Front Desk — {user.full_name}", font=("Arial", 20, "bold"))
        label.pack(side="left", padx=20, pady=10)

        logout_btn = ctk.CTkButton(self.header_frame, text="Logout", command=parent.logout, width=80)
        logout_btn.pack(side="right", padx=20, pady=10)

        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_tenants = self.tab_view.add("Tenants")
        self.tab_maintenance = self.tab_view.add("Maintenance")
        self.tab_complaints = self.tab_view.add("Complaints")

        self.setup_tenants_tab()
        self.setup_maintenance_tab()
        self.setup_complaints_tab()

    def _clear(self, frame):
        for w in frame.winfo_children(): w.destroy()

    def _badge(self, parent, text):
        color = C.get(text, "#95a5a6")
        f = ctk.CTkFrame(parent, fg_color=color, height=24, width=100)
        f.pack_propagate(False)
        f.pack(side="left", padx=5)
        ctk.CTkLabel(f, text=str(text).replace("_", " ").title(), text_color="white", font=("Arial", 11, "bold")).pack(expand=True)

    # ── Tenants Tab ──────────────────────────────────────────────────

    def setup_tenants_tab(self):
        f = self.tab_tenants
        self._clear(f)
        
        acts = ctk.CTkFrame(f)
        acts.pack(fill="x", pady=5)
        ctk.CTkButton(acts, text="Register New Tenant", command=self._register_tenant_popup).pack(side="left", padx=5)
        ctk.CTkButton(acts, text="Refresh", command=self.setup_tenants_tab).pack(side="left", padx=5)
        
        sf = ctk.CTkScrollableFrame(f, label_text="Tenant Directory")
        sf.pack(fill="both", expand=True, pady=5)
        
        try: tenants = self.admin_service.get_all_tenants()
        except: tenants = []
        
        if not tenants:
            ctk.CTkLabel(sf, text="No tenants found.").pack(pady=20)
            return

        headers = ["Name", "Email", "Phone", "Status"]
        widths = [160, 200, 120, 80]
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
             ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"), width=widths[i], anchor="w").pack(side="left", padx=5)

        for t in tenants:
            rf = ctk.CTkFrame(sf, height=45, fg_color=("gray85", "gray17"))
            rf.pack(fill="x", pady=6, padx=5)
            # Center vertically
            ctk.CTkLabel(rf, text=t['full_name'], width=widths[0], anchor="w", font=("Arial", 13)).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(rf, text=t['email'], width=widths[1], anchor="w").pack(side="left", padx=5, pady=10)
            ctk.CTkLabel(rf, text=str(t.get('phone') or '—'), width=widths[2], anchor="w").pack(side="left", padx=5, pady=10)
            
            is_active = t['is_active']
            status = "Active" if is_active else "Inactive"
            s_color = "#2ecc71" if is_active else "#95a5a6"
            ctk.CTkLabel(rf, text=status, width=widths[3], anchor="w", text_color=s_color, font=("Arial", 12, "bold")).pack(side="left", padx=5, pady=10)
            
            ctk.CTkButton(rf, text="Details", width=60, command=lambda _t=t: self._view_tenant_popup(_t)).pack(side="left", padx=10, pady=10)

    def _register_tenant_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Register Tenant")
        popup.geometry("500x650")
        
        fields = {}
        for l, k in [("Full Name", "full_name"), ("Email", "email"), ("Phone", "phone"), ("Password", "password")]:
            ctk.CTkLabel(popup, text=l, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5,0))
            e = ctk.CTkEntry(popup, width=400, show="*" if k=="password" else "")
            e.pack(padx=20, pady=(0,5))
            fields[k] = e
            
        t_labels = [("NI Number", "ni"), ("Occupation", "occupation"), ("References", "references"), ("Requirements", "reqs")]
        for l, k in t_labels:
            ctk.CTkLabel(popup, text=l, font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5,0))
            if k == "references":
                e = ctk.CTkTextbox(popup, width=400, height=60)
            else:
                e = ctk.CTkEntry(popup, width=400)
            e.pack(padx=20, pady=(0,5))
            fields[k] = e
            
        def save():
            fdata = {k: v.get("1.0", "end-1c") if isinstance(v, ctk.CTkTextbox) else v.get() for k, v in fields.items()}
            if not fdata['full_name'] or not fdata['email'] or not fdata['ni']:
                messagebox.showwarning("Error", "Required fields missing.", parent=popup)
                return
            try:
                self.admin_service.register_tenant(fdata['full_name'], fdata['email'], fdata['password'], fdata['phone'],
                    fdata['ni'], fdata['occupation'], fdata['references'], fdata['reqs'])
                messagebox.showinfo("Success", "Tenant registered.", parent=popup)
                popup.destroy()
                self.setup_tenants_tab()
            except Exception as e: messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Register", command=save, fg_color="#2ecc71").pack(pady=20)

    def _view_tenant_popup(self, t):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Details - {t['full_name']}")
        popup.geometry("400x400")
        info = f"Name: {t['full_name']}\nEmail: {t['email']}\nPhone: {t.get('phone','—')}\nNI: {t['ni_number']}\nOccupation: {t['occupation']}\nRequirements: {t['requirements']}"
        ctk.CTkLabel(popup, text=info, justify="left", font=("Arial", 14), anchor="w").pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(popup, text="References:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        refs = ctk.CTkTextbox(popup, height=100)
        refs.insert("1.0", t.get('references_txt', ''))
        refs.configure(state="disabled")
        refs.pack(fill="x", padx=20, pady=5)

    # ── Maintenance Tab ──────────────────────────────────────────────

    def setup_maintenance_tab(self):
        f = self.tab_maintenance
        self._clear(f)
        
        acts = ctk.CTkFrame(f)
        acts.pack(fill="x", pady=5)
        ctk.CTkButton(acts, text="Log New Request", command=self._log_maintenance_popup).pack(side="left", padx=5)
        ctk.CTkButton(acts, text="Refresh", command=self.setup_maintenance_tab).pack(side="left", padx=5)
        
        sf = ctk.CTkScrollableFrame(f, label_text="Maintenance Requests")
        sf.pack(fill="both", expand=True, pady=5)
        
        try: reqs = self.maint_service.get_all_requests()
        except: reqs = []
        
        if not reqs:
             ctk.CTkLabel(sf, text="No requests found.").pack(pady=20)
             return
             
        for r in reqs:
            rf = ctk.CTkFrame(sf, height=80, fg_color=("gray85", "gray17"))
            rf.pack(fill="x", pady=6, padx=5)
            
            l1 = ctk.CTkFrame(rf, fg_color="transparent")
            l1.pack(fill="x", padx=10, pady=(10, 2))
            
            self._badge(l1, r['priority'])
            self._badge(l1, r['status'])
            ctk.CTkLabel(l1, text=f"Unit: {r['unit_code']}", font=("Arial", 14, "bold")).pack(side="left", padx=15)
            
            l2 = ctk.CTkFrame(rf, fg_color="transparent")
            l2.pack(fill="x", padx=10, pady=(2, 10))
            
            ctk.CTkLabel(l2, text=f"Tenant: {r['tenant_name']}  |  {r['description']}", 
                         font=("Arial", 12), text_color="#bdc3c7", anchor="w").pack(side="left", padx=5)

    def _log_maintenance_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Log Maintenance Request")
        popup.geometry("400x450")
        
        try: leases = self.admin_service.get_all_leases()
        except: leases = []
        
        lease_map = {}
        for l in leases:
            if l['status'] == 'ACTIVE':
                 # Now we assume apartment_id is present thanks to fix in admin_service
                 aid = l.get('apartment_id')
                 if aid: 
                     key = f"Unit {l['unit_code']} - {l['tenant_name']}"
                     lease_map[key] = (l['tenant_id'], aid)

        if not lease_map:
             ctk.CTkLabel(popup, text="No active tenants/leases found.").pack(pady=20)
             return

        ctk.CTkLabel(popup, text="Select Unit/Tenant", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        unit_var = ctk.StringVar(value=list(lease_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=unit_var, values=list(lease_map.keys())).pack(fill="x", padx=20, pady=(5,0))
        
        ctk.CTkLabel(popup, text="Priority", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        prio_var = ctk.StringVar(value="MEDIUM")
        ctk.CTkOptionMenu(popup, variable=prio_var, values=["LOW", "MEDIUM", "HIGH", "URGENT"]).pack(fill="x", padx=20, pady=(5,0))
        
        ctk.CTkLabel(popup, text="Description", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        desc_box = ctk.CTkTextbox(popup, height=100)
        desc_box.pack(fill="x", padx=20, pady=(5,0))
        
        def submit():
            sel = unit_var.get()
            if not sel: return
            tid, aid = lease_map[sel]
            desc = desc_box.get("1.0", "end-1c").strip()
            if not desc: 
                messagebox.showwarning("Error", "Description required.", parent=popup)
                return
            try:
                self.maint_service.submit_maintenance_request(tid, aid, desc, prio_var.get())
                messagebox.showinfo("Success", "Logged.", parent=popup)
                popup.destroy()
                self.setup_maintenance_tab()
            except Exception as e: messagebox.showerror("Error", str(e), parent=popup)
            
        ctk.CTkButton(popup, text="Submit", command=submit).pack(pady=20)

    # ── Complaints Tab ───────────────────────────────────────────────

    def setup_complaints_tab(self):
        f = self.tab_complaints
        self._clear(f)
        
        acts = ctk.CTkFrame(f)
        acts.pack(fill="x", pady=5)
        ctk.CTkButton(acts, text="Log New Complaint", command=self._log_complaint_popup).pack(side="left", padx=5)
        ctk.CTkButton(acts, text="Refresh", command=self.setup_complaints_tab).pack(side="left", padx=5)
        
        sf = ctk.CTkScrollableFrame(f, label_text="Complaints")
        sf.pack(fill="both", expand=True, pady=5)

        try: complaints = self.admin_service.get_all_complaints()
        except: complaints = []

        if not complaints:
            ctk.CTkLabel(sf, text="No complaints found.").pack(pady=20)
            return

        for c in complaints:
            rf = ctk.CTkFrame(sf, fg_color=("gray85", "gray17"))
            rf.pack(fill="x", pady=6, padx=5)
            
            l1 = ctk.CTkFrame(rf, fg_color="transparent")
            l1.pack(fill="x", padx=10, pady=(10, 2))
            
            self._badge(l1, c['status'])
            ctk.CTkLabel(l1, text=f"Tenant: {c['tenant_name']}", font=("Arial", 14, "bold")).pack(side="left", padx=15)
            
            l2 = ctk.CTkFrame(rf, fg_color="transparent")
            l2.pack(fill="x", padx=10, pady=(2, 10))
            
            desc = c['description'][:100] + "..." if len(c['description']) > 100 else c['description']
            ctk.CTkLabel(l2, text=desc, font=("Arial", 12), text_color="#bdc3c7", wraplength=500, justify="left").pack(anchor="w", padx=5)

    def _log_complaint_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Log Complaint")
        popup.geometry("400x350")
        
        try: leases = self.admin_service.get_all_leases()
        except: leases = []
        
        lease_map = {}
        for l in leases:
            if l['status'] == 'ACTIVE':
                 key = f"{l['tenant_name']} (Unit {l['unit_code']})"
                 lease_map[key] = l['tenant_id']

        if not lease_map:
             ctk.CTkLabel(popup, text="No active tenants.").pack(pady=20)
             return

        ctk.CTkLabel(popup, text="Select Tenant", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        t_var = ctk.StringVar(value=list(lease_map.keys())[0])
        ctk.CTkOptionMenu(popup, variable=t_var, values=list(lease_map.keys())).pack(fill="x", padx=20, pady=(5,0))
        
        ctk.CTkLabel(popup, text="Details", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        desc_box = ctk.CTkTextbox(popup, height=100)
        desc_box.pack(fill="x", padx=20, pady=(5,0))
        
        def submit():
            tid = lease_map[t_var.get()]
            desc = desc_box.get("1.0", "end-1c").strip()
            if not desc: 
                messagebox.showwarning("Error", "Description required.", parent=popup)
                return
            try:
                self.maint_service.submit_complaint(tid, desc)
                messagebox.showinfo("Success", "Logged.", parent=popup)
                popup.destroy()
                self.setup_complaints_tab()
            except Exception as e: messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Submit", command=submit, fg_color="#e74c3c").pack(pady=20)
