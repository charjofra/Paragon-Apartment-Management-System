import customtkinter as ctk
from models import User
from services.tenant_service import TenantService
from typing import TYPE_CHECKING
from tkinter import messagebox
from datetime import datetime, date

if TYPE_CHECKING:
    from views.gui import App

# ── Status colour + human-readable maps ───────────────────────────

COMPLAINT_STATUS_COLOURS = {
    "OPEN":        "#3498db",   # blue
    "IN_PROGRESS": "#f1c40f",   # yellow
    "RESOLVED":    "#2ecc71",   # green
    "CLOSED":      "#e74c3c",   # red
}

MAINTENANCE_STATUS_COLOURS = {
    "REPORTED":    "#3498db",   # blue
    "TRIAGED":     "#9b59b6",   # purple
    "SCHEDULED":   "#f39c12",   # orange
    "IN_PROGRESS": "#f1c40f",   # yellow
    "RESOLVED":    "#2ecc71",   # green
    "CLOSED":      "#e74c3c",   # red
}

PRIORITY_COLOURS = {
    "LOW":    "#2ecc71",
    "MEDIUM": "#f39c12",
    "HIGH":   "#e67e22",
    "URGENT": "#e74c3c",
}

_DISPLAY_OVERRIDES = {
    "TRIAGED": "Assigned",
}

def _humanise(text: str) -> str:
    """REPORTED -> Reported, IN_PROGRESS -> In Progress, TRIAGED -> Assigned, etc."""
    if text in _DISPLAY_OVERRIDES:
        return _DISPLAY_OVERRIDES[text]
    return text.replace("_", " ").title()

def _uk_date(value) -> str:
    """Convert a date/datetime value to DD/MM/YYYY."""
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    # Fallback: try parsing common string formats
    text = str(value)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:len(fmt.replace("%", "0"))], fmt).strftime(
                "%d/%m/%Y %H:%M" if " " in fmt else "%d/%m/%Y"
            )
        except (ValueError, IndexError):
            continue
    return text


class TenantDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.service = TenantService(user.tenant_id)
        self.details = self.service.get_tenant_details()

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        label = ctk.CTkLabel(self.header_frame, text=f"Welcome, {user.full_name}",
                             font=("Arial", 20, "bold"))
        label.pack(side="left", padx=20, pady=10)

        logout_btn = ctk.CTkButton(self.header_frame, text="Logout",
                                    command=parent.logout, width=80)
        logout_btn.pack(side="right", padx=20, pady=10)

        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_overview = self.tab_view.add("Overview")
        self.tab_payments = self.tab_view.add("Payments")
        self.tab_maintenance = self.tab_view.add("Maintenance")
        self.tab_complaints = self.tab_view.add("Complaints")

        self.setup_overview_tab()
        self.setup_payments_tab()
        self.setup_maintenance_tab()
        self.setup_complaints_tab()

        self.after(500, self.check_overdue_payments)

    # ── helpers ────────────────────────────────────────────────────────

    def _clear(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    @staticmethod
    def _status_badge(parent, text: str, colour: str, width: int = 110):
        badge = ctk.CTkFrame(parent, fg_color=colour, corner_radius=6, width=width, height=26)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=5)
        ctk.CTkLabel(badge, text=_humanise(text), text_color="white",
                     font=("Arial", 11, "bold")).pack(expand=True)
        return badge

    @staticmethod
    def _priority_badge(parent, text: str, width: int = 80):
        colour = PRIORITY_COLOURS.get(text, "#95a5a6")
        badge = ctk.CTkFrame(parent, fg_color=colour, corner_radius=6, width=width, height=26)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=5)
        ctk.CTkLabel(badge, text=_humanise(text), text_color="white",
                     font=("Arial", 11, "bold")).pack(expand=True)
        return badge

    # ── Overdue check ─────────────────────────────────────────────────

    def check_overdue_payments(self):
        overdue = self.service.get_unpaid_invoices(overdue_only=True)
        if overdue:
            count = len(overdue)
            total_amount = sum(float(inv['amount_due']) for inv in overdue)
            messagebox.showwarning(
                "Overdue Payments Alert",
                f"Attention: You have {count} overdue invoice(s) totalling £{total_amount:.2f}.\n"
                "Please check the Payments tab to settle these immediately."
            )

    # ── Overview ──────────────────────────────────────────────────────

    def setup_overview_tab(self):
        frame = self.tab_overview
        self._clear(frame)

        info_text = (
            f"  Name:  {self.user.full_name}\n"
            f"  Email:  {self.user.email}\n"
            f"  NI Number:  {self.details.get('ni_number', 'N/A')}\n"
            f"  Occupation:  {self.details.get('occupation', 'N/A')}"
        )
        ctk.CTkLabel(frame, text="Your Information",
                     font=("Arial", 16, "bold")).pack(pady=10, anchor="w")
        ctk.CTkLabel(frame, text=info_text, justify="left").pack(pady=5, anchor="w")

        unpaid = self.service.get_unpaid_invoices()
        if unpaid:
            alert_frame = ctk.CTkFrame(frame, fg_color="#e74c3c")
            alert_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(alert_frame,
                         text=f"You have {len(unpaid)} unpaid invoice(s)!",
                         text_color="white").pack(pady=5)

    # ── Payments ──────────────────────────────────────────────────────

    def setup_payments_tab(self):
        frame = self.tab_payments
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Make Payment",
                       command=self.make_payment_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="View Payment Graph",
                       command=lambda: messagebox.showinfo("Info", "Graph feature WIP")).pack(side="left", padx=5)

        history_frame = ctk.CTkScrollableFrame(frame, label_text="Payment History")
        history_frame.pack(fill="both", expand=True, pady=10)

        payments = self.service.get_payment_history()

        if not payments:
            ctk.CTkLabel(history_frame, text="No payment history found.").pack(pady=20)
        else:
            headers = ["Date", "Amount", "Method", "Due Date"]
            widths = [140, 100, 120, 110]
            hf = ctk.CTkFrame(history_frame)
            hf.pack(fill="x")
            for i, h in enumerate(headers):
                ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"),
                             width=widths[i]).pack(side="left", padx=5)

            for p in payments:
                row = ctk.CTkFrame(history_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=_uk_date(p['paid_at']),
                             width=widths[0]).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"£{p['amount_paid']}",
                             width=widths[1]).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=_humanise(p['method']),
                             width=widths[2]).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=_uk_date(p['due_date']),
                             width=widths[3]).pack(side="left", padx=5)

    # ── Maintenance ───────────────────────────────────────────────────

    def setup_maintenance_tab(self):
        frame = self.tab_maintenance
        self._clear(frame)

        # Input bar
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(input_frame, text="New Request:").pack(side="left", padx=5)
        self.mnt_desc = ctk.CTkEntry(input_frame, placeholder_text="Describe the issue…", width=300)
        self.mnt_desc.pack(side="left", padx=5)

        self.mnt_priority = ctk.CTkOptionMenu(input_frame,
                                               values=["LOW", "MEDIUM", "HIGH", "URGENT"])
        self.mnt_priority.set("MEDIUM")
        self.mnt_priority.pack(side="left", padx=5)

        self.active_leases = self.service.get_active_lease_info()
        self.lease_options = {f"{l['unit_code']} ({l['city']})": l['apartment_id']
                              for l in self.active_leases}

        if len(self.lease_options) > 1:
            self.lease_selector = ctk.CTkComboBox(input_frame,
                                                   values=list(self.lease_options.keys()))
            self.lease_selector.pack(side="left", padx=5)
        else:
            self.lease_selector = None

        ctk.CTkButton(input_frame, text="Submit",
                       command=self.submit_maintenance).pack(side="left", padx=5)

        # Existing requests
        list_frame = ctk.CTkScrollableFrame(frame, label_text="Your Requests")
        list_frame.pack(fill="both", expand=True, pady=5)

        requests = self.service.get_maintenance_requests()
        if not requests:
            ctk.CTkLabel(list_frame, text="No maintenance requests yet.").pack(pady=20)
        else:
            for req in requests:
                # Card-style container per request
                card = ctk.CTkFrame(list_frame)
                card.pack(fill="x", pady=4, padx=5)

                # Top row: date, description, badges
                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=8, pady=(6, 2))

                ctk.CTkLabel(top, text=_uk_date(req['date_created']),
                             width=100, font=("Arial", 11)).pack(side="left", padx=(0, 8))

                status_colour = MAINTENANCE_STATUS_COLOURS.get(req['status'], "#95a5a6")
                self._status_badge(top, req['status'], status_colour)
                self._priority_badge(top, req['priority'])

                if req.get('scheduled_at'):
                    ctk.CTkLabel(top, text=f"Scheduled: {_uk_date(req['scheduled_at'])}",
                                 font=("Arial", 11)).pack(side="right", padx=5)

                # Description
                ctk.CTkLabel(card, text=req['description'], anchor="w",
                             wraplength=550, justify="left",
                             font=("Arial", 12)).pack(fill="x", padx=10, pady=(2, 4))

                # Resolution details (if resolved)
                if req.get('resolution_details'):
                    res_frame = ctk.CTkFrame(card, fg_color=("#d5f5e3", "#1a3a2a"),
                                              corner_radius=4)
                    res_frame.pack(fill="x", padx=10, pady=(0, 6))
                    ctk.CTkLabel(res_frame, text="Resolution",
                                 font=("Arial", 11, "bold")).pack(anchor="w", padx=8, pady=(4, 0))
                    ctk.CTkLabel(res_frame, text=req['resolution_details'],
                                 anchor="w", wraplength=520, justify="left",
                                 font=("Arial", 11)).pack(fill="x", padx=8, pady=(0, 2))
                    extras = []
                    if req.get('resolved_at'):
                        extras.append(f"Resolved: {_uk_date(req['resolved_at'])}")
                    if req.get('time_taken_hours'):
                        extras.append(f"Time: {req['time_taken_hours']}h")
                    if req.get('cost') and float(req['cost']) > 0:
                        extras.append(f"Cost: £{req['cost']}")
                    if extras:
                        ctk.CTkLabel(res_frame, text="  |  ".join(extras),
                                     font=("Arial", 10)).pack(anchor="w", padx=8, pady=(0, 4))

    # ── Complaints ────────────────────────────────────────────────────

    def setup_complaints_tab(self):
        frame = self.tab_complaints
        self._clear(frame)

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", pady=10)

        self.comp_desc = ctk.CTkEntry(input_frame,
                                       placeholder_text="Describe your complaint…", width=400)
        self.comp_desc.pack(side="left", padx=5)
        ctk.CTkButton(input_frame, text="Submit",
                       command=self.submit_complaint).pack(side="left", padx=5)

        list_frame = ctk.CTkScrollableFrame(frame, label_text="Your Complaints")
        list_frame.pack(fill="both", expand=True, pady=5)

        complaints = self.service.get_complaints()
        if not complaints:
            ctk.CTkLabel(list_frame, text="No complaints submitted yet.").pack(pady=20)
        else:
            hf = ctk.CTkFrame(list_frame)
            hf.pack(fill="x")
            for h, w in [("Date", 120), ("Description", 340), ("Status", 120)]:
                ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"), width=w).pack(side="left", padx=5)

            for c in complaints:
                row = ctk.CTkFrame(list_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=_uk_date(c['date_created']),
                             width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=c['description'], width=340,
                             anchor="w").pack(side="left", padx=5)

                colour = COMPLAINT_STATUS_COLOURS.get(c['status'], "#95a5a6")
                self._status_badge(row, c['status'], colour)

    # ── Actions ───────────────────────────────────────────────────────

    def submit_maintenance(self):
        desc = self.mnt_desc.get().strip()
        priority = self.mnt_priority.get()
        if not desc:
            messagebox.showwarning("Input Error", "Please provide a description.")
            return

        apartment_id = None
        if self.lease_selector:
            selected_label = self.lease_selector.get()
            apartment_id = self.lease_options.get(selected_label)
        elif self.active_leases:
            apartment_id = self.active_leases[0]['apartment_id']

        if not apartment_id:
            messagebox.showerror("Error", "No active apartment found to submit request for.")
            return

        if self.service.submit_maintenance_request(desc, priority, apartment_id):
            messagebox.showinfo("Success", "Maintenance request submitted.")
            self.setup_maintenance_tab()
        else:
            messagebox.showerror("Error", "Failed to submit request.")

    def submit_complaint(self):
        desc = self.comp_desc.get().strip()
        if not desc:
            messagebox.showwarning("Input Error", "Please describe your complaint.")
            return
        if self.service.submit_complaint(desc):
            messagebox.showinfo("Success", "Complaint submitted.")
            self.setup_complaints_tab()
        else:
            messagebox.showerror("Error",
                                 "Could not submit complaint. Do you have an active lease?")

    def make_payment_popup(self):
        unpaid_invoices = self.service.get_unpaid_invoices()
        if not unpaid_invoices:
            messagebox.showinfo("Info", "You have no unpaid invoices.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Make Payment")
        popup.geometry("420x320")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Select Invoice to Pay:",
                     font=("Arial", 14, "bold")).pack(pady=10)

        invoice_options = {
            f"Inv #{i['invoice_id']} — £{i['amount_due']} (Due: {_uk_date(i['due_date'])})": i
            for i in unpaid_invoices
        }
        selected_invoice = ctk.StringVar(value=list(invoice_options.keys())[0])
        ctk.CTkOptionMenu(popup, variable=selected_invoice,
                           values=list(invoice_options.keys())).pack(pady=5)

        ctk.CTkLabel(popup, text="Card Number (16 digits):").pack(pady=(15, 5))
        card_entry = ctk.CTkEntry(popup, placeholder_text="XXXX XXXX XXXX XXXX")
        card_entry.pack(pady=5)

        def process_payment():
            key = selected_invoice.get()
            inv_data = invoice_options[key]
            card_num = card_entry.get().replace(" ", "")

            if not card_num.isdigit() or len(card_num) != 16:
                messagebox.showerror("Error", "Invalid card number. Must be 16 digits.",
                                     parent=popup)
                return

            success = self.service.pay_invoice(inv_data['invoice_id'],
                                               float(inv_data['amount_due']))
            if success:
                messagebox.showinfo("Success", "Payment successful!", parent=popup)
                popup.destroy()
                self.setup_payments_tab()
                self.setup_overview_tab()
            else:
                messagebox.showerror("Error", "Payment failed.", parent=popup)

        ctk.CTkButton(popup, text="Pay Now", command=process_payment).pack(pady=20)