import customtkinter as ctk
from models import User
from services.tenant_service import TenantService
from typing import TYPE_CHECKING
from tkinter import messagebox
from datetime import datetime, date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
    "UNPAID":    "#e67e22",
    "PAID":      "#2ecc71",
    "LATE":      "#e74c3c",
    "ACTIVE":                "#2ecc71",
    "ENDED":                 "#e74c3c",
    "TERMINATION_REQUESTED": "#f39c12",
}
_GREY = "#95a5a6"

_DISPLAY_OVERRIDES = {
    "TRIAGED": "Assigned",
    "TERMINATION_REQUESTED": "Early Leave Pending",
}

def _humanise(text: str) -> str:
    if text in _DISPLAY_OVERRIDES:
        return _DISPLAY_OVERRIDES[text]
    return text.replace("_", " ").title()

def _uk_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
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
        self.tab_leases = self.tab_view.add("Leases")
        self.tab_payments = self.tab_view.add("Payments")
        self.tab_maintenance = self.tab_view.add("Maintenance")
        self.tab_complaints = self.tab_view.add("Complaints")
        self.tab_notifications = self.tab_view.add("Notifications")

        self.setup_overview_tab()
        self.setup_leases_tab()
        self.setup_payments_tab()
        self.setup_maintenance_tab()
        self.setup_complaints_tab()
        self.setup_notifications_tab()

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
        colour = C.get(text, _GREY)
        badge = ctk.CTkFrame(parent, fg_color=colour, corner_radius=6, width=width, height=26)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=5)
        ctk.CTkLabel(badge, text=_humanise(text), text_color="white",
                     font=("Arial", 11, "bold")).pack(expand=True)
        return badge

    def _embed_figure(self, parent, fig):
        """Embed a matplotlib Figure into a CTk frame."""
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        return canvas

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

    # ══════════════════════════════════════════════════════════════════
    #  OVERVIEW TAB
    # ══════════════════════════════════════════════════════════════════

    def setup_overview_tab(self):
        frame = self.tab_overview
        self._clear(frame)

        # ── Personal info ──
        ctk.CTkLabel(frame, text="Your Information",
                     font=("Arial", 16, "bold")).pack(pady=(10, 5), anchor="w", padx=10)

        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=5)
        info_text = (
            f"  Name:  {self.user.full_name}\n"
            f"  Email:  {self.user.email}\n"
            f"  NI Number:  {self.details.get('ni_number', 'N/A')}\n"
            f"  Occupation:  {self.details.get('occupation', 'N/A')}"
        )
        ctk.CTkLabel(info_frame, text=info_text, justify="left",
                     font=("Arial", 13)).pack(pady=8, padx=10, anchor="w")

        # ── Active lease summary ──
        active_leases = self.service.get_active_lease_info()
        if active_leases:
            ctk.CTkLabel(frame, text="Active Lease(s)",
                         font=("Arial", 16, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
            for al in active_leases:
                lf = ctk.CTkFrame(frame)
                lf.pack(fill="x", padx=10, pady=3)
                ctk.CTkLabel(lf, text=f"  Unit: {al['unit_code']}  |  "
                             f"City: {al['city']}  |  Address: {al.get('address', 'N/A')}",
                             font=("Arial", 13)).pack(pady=6, padx=10, anchor="w")

        # ── Unpaid invoice alert ──
        unpaid = self.service.get_unpaid_invoices()
        if unpaid:
            alert_frame = ctk.CTkFrame(frame, fg_color="#e74c3c")
            alert_frame.pack(fill="x", padx=10, pady=10)
            total = sum(float(i['amount_due']) for i in unpaid)
            ctk.CTkLabel(alert_frame,
                         text=f"⚠  You have {len(unpaid)} unpaid invoice(s) totalling £{total:.2f}",
                         text_color="white", font=("Arial", 13, "bold")).pack(pady=8)

        # ── Quick stats cards ──
        payments = self.service.get_payment_history()
        requests = self.service.get_maintenance_requests()
        complaints = self.service.get_complaints()

        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=10)
        items = [
            ("Total Payments", len(payments)),
            ("Open Requests", sum(1 for r in requests if r['status'] not in ('RESOLVED', 'CLOSED'))),
            ("Open Complaints", sum(1 for c in complaints if c['status'] not in ('RESOLVED', 'CLOSED'))),
        ]
        for idx, (title, value) in enumerate(items):
            card = ctk.CTkFrame(cards_frame)
            card.grid(row=0, column=idx, padx=8, pady=5, sticky="nsew")
            cards_frame.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(8, 2))
            ctk.CTkLabel(card, text=str(value), font=("Arial", 22, "bold")).pack(pady=(2, 8))

    # ══════════════════════════════════════════════════════════════════
    #  LEASES TAB
    # ══════════════════════════════════════════════════════════════════

    def setup_leases_tab(self):
        frame = self.tab_leases
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_leases_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Your Lease Agreements")
        sf.pack(fill="both", expand=True, pady=5)

        leases = self.service.get_all_leases()
        if not leases:
            ctk.CTkLabel(sf, text="No lease agreements found.").pack(pady=20)
            return

        for lease in leases:
            card = ctk.CTkFrame(sf)
            card.pack(fill="x", pady=5, padx=5)

            # Top row: unit + status badge
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(8, 4))

            ctk.CTkLabel(top, text=f"{lease['unit_code']} — {lease['apt_type']}",
                         font=("Arial", 14, "bold")).pack(side="left")
            s_colour = C.get(lease['status'], _GREY)
            self._status_badge(top, lease['status'], s_colour, width=140)

            # Details
            details_frame = ctk.CTkFrame(card, fg_color="transparent")
            details_frame.pack(fill="x", padx=10, pady=(0, 4))

            info = (
                f"City: {lease['city']}  |  "
                f"Rooms: {lease['rooms']}  |  "
                f"Rent: £{lease['monthly_rent']}  |  "
                f"Start: {_uk_date(lease['start_date'])}  |  "
                f"End: {_uk_date(lease['end_date'])}"
            )
            ctk.CTkLabel(details_frame, text=info, font=("Arial", 12)).pack(anchor="w")

            # Early termination info
            if lease.get('early_leave_notice_date'):
                et_frame = ctk.CTkFrame(card, fg_color=("#fff3cd", "#3d3520"), corner_radius=4)
                et_frame.pack(fill="x", padx=10, pady=(0, 4))
                et_text = (
                    f"  Early Leave Requested  |  "
                    f"Notice: {_uk_date(lease['early_leave_notice_date'])}  |  "
                    f"Requested End: {_uk_date(lease['early_leave_requested_end'])}  |  "
                    f"Penalty: £{lease['early_leave_penalty']}"
                )
                ctk.CTkLabel(et_frame, text=et_text, font=("Arial", 11)).pack(pady=5, anchor="w")

            # Early termination button (only for ACTIVE leases without existing request)
            if lease['status'] == 'ACTIVE' and not lease.get('early_leave_notice_date'):
                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(fill="x", padx=10, pady=(0, 8))
                ctk.CTkButton(btn_frame, text="Request Early Termination",
                               fg_color="#e74c3c", hover_color="#c0392b",
                               command=lambda _l=lease: self._early_termination_popup(_l)
                               ).pack(side="left")

    def _early_termination_popup(self, lease):
        popup = ctk.CTkToplevel(self)
        popup.title("Request Early Termination")
        popup.geometry("460x320")
        popup.transient(self)
        popup.grab_set()

        rent = float(lease["monthly_rent"])
        penalty = round(rent * 0.05, 2)
        notice_date = date.today()
        requested_end = notice_date + __import__('datetime').timedelta(days=30)

        ctk.CTkLabel(popup, text="Early Termination Request",
                     font=("Arial", 16, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(popup,
                     text=f"Unit: {lease['unit_code']} — {lease['apt_type']}",
                     font=("Arial", 13)).pack(pady=3)
        ctk.CTkLabel(popup,
                     text=f"Monthly Rent: £{rent:.2f}",
                     font=("Arial", 13)).pack(pady=3)

        # Warning frame
        warn = ctk.CTkFrame(popup, fg_color="#e74c3c", corner_radius=8)
        warn.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(warn, text="⚠  Early Termination Terms", text_color="white",
                     font=("Arial", 13, "bold")).pack(pady=(8, 3))
        ctk.CTkLabel(warn, text=f"• 1 month notice period required", text_color="white",
                     font=("Arial", 12)).pack(anchor="w", padx=15)
        ctk.CTkLabel(warn, text=f"• Penalty of 5% monthly rent: £{penalty:.2f}", text_color="white",
                     font=("Arial", 12)).pack(anchor="w", padx=15)
        ctk.CTkLabel(warn, text=f"• Earliest leave date: {requested_end.strftime('%d/%m/%Y')}",
                     text_color="white", font=("Arial", 12)).pack(anchor="w", padx=15, pady=(0, 8))

        def confirm():
            if not messagebox.askyesno(
                "Confirm Early Termination",
                f"Are you sure you want to request early termination?\n\n"
                f"A penalty of £{penalty:.2f} will apply and you must give "
                f"1 month notice (leave date: {requested_end.strftime('%d/%m/%Y')}).",
                parent=popup
            ):
                return
            result = self.service.request_early_termination(lease["lease_id"])
            if result["success"]:
                messagebox.showinfo(
                    "Request Submitted",
                    f"Early termination requested.\n"
                    f"Leave date: {result['end_date']}\n"
                    f"Penalty: £{result['penalty']:.2f}",
                    parent=popup
                )
                popup.destroy()
                self.setup_leases_tab()
                self.setup_overview_tab()
            else:
                messagebox.showerror("Error", result.get("error", "Failed."), parent=popup)

        ctk.CTkButton(popup, text="Confirm Early Termination",
                       fg_color="#e74c3c", hover_color="#c0392b",
                       command=confirm).pack(pady=15)

    # ══════════════════════════════════════════════════════════════════
    #  PAYMENTS TAB
    # ══════════════════════════════════════════════════════════════════

    def setup_payments_tab(self):
        frame = self.tab_payments
        self._clear(frame)

        # Action buttons
        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Make Payment",
                       command=self.make_payment_popup).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Payment History Graph",
                       command=self._show_payment_history_graph).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Vs Neighbours",
                       command=self._show_neighbour_comparison_graph).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Late Payments (Property)",
                       command=self._show_late_payments_graph).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_payments_tab).pack(side="left", padx=5)

        # Unpaid invoices alert
        unpaid = self.service.get_unpaid_invoices()
        if unpaid:
            alert = ctk.CTkFrame(frame, fg_color="#e74c3c")
            alert.pack(fill="x", padx=5, pady=5)
            total = sum(float(i['amount_due']) for i in unpaid)
            ctk.CTkLabel(alert,
                         text=f"⚠  {len(unpaid)} unpaid invoice(s) — £{total:.2f} outstanding",
                         text_color="white", font=("Arial", 12, "bold")).pack(pady=6)

        # Payment history table
        history_frame = ctk.CTkScrollableFrame(frame, label_text="Payment History")
        history_frame.pack(fill="both", expand=True, pady=5)

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
                             width=widths[i], anchor="w").pack(side="left", padx=5)

            for p in payments:
                row = ctk.CTkFrame(history_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=_uk_date(p['paid_at']),
                             width=widths[0], anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"£{p['amount_paid']}",
                             width=widths[1], anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=_humanise(p['method']),
                             width=widths[2], anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=_uk_date(p['due_date']),
                             width=widths[3], anchor="w").pack(side="left", padx=5)

    # ── Payment Graph: History ────────────────────────────────────────

    def _show_payment_history_graph(self):
        data = self.service.get_monthly_payment_data()
        if not data:
            messagebox.showinfo("Info", "No payment data to display.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Payment History — Monthly")
        popup.geometry("700x450")
        popup.transient(self)
        popup.grab_set()

        months = [d['month'] for d in data]
        totals = [float(d['total']) for d in data]

        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(months, totals, color="#3498db", edgecolor="white")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount (£)")
        ax.set_title("Your Monthly Payments")
        for bar, val in zip(bars, totals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f"£{val:.0f}", ha='center', va='bottom', fontsize=8)
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()

        self._embed_figure(popup, fig)

    # ── Payment Graph: Vs Neighbours ──────────────────────────────────

    def _show_neighbour_comparison_graph(self):
        data = self.service.get_neighbour_comparison()
        t_data = data.get("tenant", [])
        n_data = data.get("neighbours", [])

        if not t_data and not n_data:
            messagebox.showinfo("Info", "Not enough data for comparison.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Your Payments vs Neighbours")
        popup.geometry("750x470")
        popup.transient(self)
        popup.grab_set()

        # Merge months from both datasets
        all_months = sorted(set(
            [d['month'] for d in t_data] + [d['month'] for d in n_data]
        ))
        t_map = {d['month']: float(d['total']) for d in t_data}
        n_map = {d['month']: float(d['avg_total']) for d in n_data}

        t_vals = [t_map.get(m, 0) for m in all_months]
        n_vals = [n_map.get(m, 0) for m in all_months]

        fig = Figure(figsize=(7.5, 4.2), dpi=100)
        ax = fig.add_subplot(111)
        import numpy as np
        x = np.arange(len(all_months))
        w = 0.35
        ax.bar(x - w/2, t_vals, w, label="You", color="#3498db")
        ax.bar(x + w/2, n_vals, w, label="Neighbours (Avg)", color="#e67e22")
        ax.set_xticks(x)
        ax.set_xticklabels(all_months, rotation=45, ha='right')
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount (£)")
        ax.set_title("Your Payments vs Close Neighbours")
        ax.legend()
        fig.tight_layout()

        self._embed_figure(popup, fig)

    # ── Payment Graph: Late Payments per Property ─────────────────────

    def _show_late_payments_graph(self):
        data = self.service.get_late_payments_by_property()
        if not data:
            messagebox.showinfo("Info", "No late payment data to display.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Late Payments — Per Property")
        popup.geometry("700x450")
        popup.transient(self)
        popup.grab_set()

        units = [d['unit_code'] for d in data]
        counts = [int(d['late_count']) for d in data]

        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(units, counts, color="#e74c3c", edgecolor="white")
        ax.set_xlabel("Property (Unit)")
        ax.set_ylabel("Late Payment Count")
        ax.set_title("Late Payments Per Property")
        for bar, val in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()

        self._embed_figure(popup, fig)

    # ══════════════════════════════════════════════════════════════════
    #  MAINTENANCE TAB
    # ══════════════════════════════════════════════════════════════════

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
                card = ctk.CTkFrame(list_frame)
                card.pack(fill="x", pady=4, padx=5)

                # Top row
                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=8, pady=(6, 2))

                ctk.CTkLabel(top, text="Issue",
                             font=("Arial", 12, "bold")).pack(side="left", padx=(0, 6))
                self._priority_badge(top, req['priority'])
                status_colour = C.get(req['status'], _GREY)
                self._status_badge(top, req['status'], status_colour)
                ctk.CTkLabel(top, text=_uk_date(req['date_created']),
                             font=("Arial", 11)).pack(side="left", padx=(8, 0))

                if req.get('scheduled_at'):
                    ctk.CTkLabel(top, text=f"Scheduled: {_uk_date(req['scheduled_at'])}",
                                 font=("Arial", 11)).pack(side="right", padx=5)

                # Description
                ctk.CTkLabel(card, text=req['description'], anchor="w",
                             wraplength=550, justify="left",
                             font=("Arial", 12)).pack(fill="x", padx=10, pady=(2, 4))

                # Resolution details
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

    # ══════════════════════════════════════════════════════════════════
    #  COMPLAINTS TAB
    # ══════════════════════════════════════════════════════════════════

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
                ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"), width=w, anchor="w").pack(side="left", padx=5)

            for c in complaints:
                row = ctk.CTkFrame(list_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=_uk_date(c['date_created']),
                             width=120, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=c['description'], width=340,
                             anchor="w").pack(side="left", padx=5)
                colour = C.get(c['status'], _GREY)
                self._status_badge(row, c['status'], colour)

    # ══════════════════════════════════════════════════════════════════
    #  NOTIFICATIONS TAB
    # ══════════════════════════════════════════════════════════════════

    def setup_notifications_tab(self):
        frame = self.tab_notifications
        self._clear(frame)

        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(actions, text="Refresh",
                       command=self.setup_notifications_tab).pack(side="left", padx=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Your Notifications")
        sf.pack(fill="both", expand=True, pady=5)

        notifications = self.service.get_notifications()
        if not notifications:
            ctk.CTkLabel(sf, text="No notifications.").pack(pady=20)
            return

        type_colors = {
            "LATE_PAYMENT": "#e74c3c",
            "MAINTENANCE_UPDATE": "#f39c12",
            "LEASE_UPDATE": "#3498db",
            "GENERAL": "#95a5a6",
        }

        for n in notifications:
            card = ctk.CTkFrame(sf)
            card.pack(fill="x", pady=3, padx=5)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=8, pady=(6, 2))

            n_type = n.get('type', 'GENERAL')
            colour = type_colors.get(n_type, _GREY)
            badge = ctk.CTkFrame(top, fg_color=colour, corner_radius=6, width=130, height=24)
            badge.pack_propagate(False)
            badge.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(badge, text=_humanise(n_type), text_color="white",
                         font=("Arial", 10, "bold")).pack(expand=True)

            ctk.CTkLabel(top, text=_uk_date(n['date_created']),
                         font=("Arial", 11)).pack(side="right", padx=5)

            ctk.CTkLabel(card, text=n['message'], anchor="w", wraplength=550,
                         justify="left", font=("Arial", 12)).pack(fill="x", padx=10, pady=(2, 8))

    # ══════════════════════════════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════════════════════════════

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
        popup.geometry("450x420")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Make a Payment",
                     font=("Arial", 16, "bold")).pack(pady=(15, 5))

        ctk.CTkLabel(popup, text="Select Invoice:",
                     font=("Arial", 13)).pack(anchor="w", padx=20, pady=(10, 2))

        invoice_options = {
            f"Inv #{i['invoice_id']} — £{i['amount_due']} (Due: {_uk_date(i['due_date'])})": i
            for i in unpaid_invoices
        }
        selected_invoice = ctk.StringVar(value=list(invoice_options.keys())[0])
        ctk.CTkOptionMenu(popup, variable=selected_invoice,
                           values=list(invoice_options.keys()), width=400).pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Card Number (16 digits):",
                     font=("Arial", 13)).pack(anchor="w", padx=20, pady=(15, 2))
        card_entry = ctk.CTkEntry(popup, placeholder_text="XXXX XXXX XXXX XXXX", width=400)
        card_entry.pack(padx=20, pady=5)

        ctk.CTkLabel(popup, text="Expiry (MM/YY):",
                     font=("Arial", 13)).pack(anchor="w", padx=20, pady=(10, 2))
        expiry_entry = ctk.CTkEntry(popup, placeholder_text="MM/YY", width=400)
        expiry_entry.pack(padx=20, pady=5)

        def process_payment():
            key = selected_invoice.get()
            inv_data = invoice_options[key]
            card_num = card_entry.get().replace(" ", "").replace("-", "")
            expiry = expiry_entry.get().strip()

            # Card validation
            if not card_num.isdigit() or len(card_num) != 16:
                messagebox.showerror("Error", "Invalid card number. Must be 16 digits.",
                                     parent=popup)
                return

            # Basic expiry validation
            if not expiry or len(expiry) < 4:
                messagebox.showerror("Error", "Please enter a valid expiry date (MM/YY).",
                                     parent=popup)
                return

            success = self.service.pay_invoice(inv_data['invoice_id'],
                                               float(inv_data['amount_due']))
            if success:
                messagebox.showinfo("Success",
                                    f"Payment of £{inv_data['amount_due']} successful!",
                                    parent=popup)
                popup.destroy()
                self.setup_payments_tab()
                self.setup_overview_tab()
            else:
                messagebox.showerror("Error", "Payment failed.", parent=popup)

        ctk.CTkButton(popup, text="Pay Now", command=process_payment,
                       width=200).pack(pady=20)