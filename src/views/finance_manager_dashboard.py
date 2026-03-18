import customtkinter as ctk
from models.user import User
from services.finance_service import FinanceService
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

C = {
    "UNPAID":    "#e67e22",
    "PAID":      "#2ecc71",
    "LATE":      "#e74c3c",
    "CANCELLED": "#95a5a6",
    "CASH": "#3498db",
    "CARD": "#9b59b6",
    "BANK_TRANSFER": "#f1c40f",
    "CHEQUE": "#1abc9c",
    "OTHER": "#34495e",
    "ALL": "#7f8c8d" 
}
_GREY = "#95a5a6"

def _uk_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    text = str(value)
    # Try parsing string iso format
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:len(fmt)], fmt).strftime(
                "%d/%m/%Y %H:%M" if " " in fmt else "%d/%m/%Y"
            )
        except (ValueError, IndexError):
            continue
    return text

class FinanceManagerDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.service = FinanceService(user.user_id)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        label = ctk.CTkLabel(self.header_frame, text=f"Finance Dashboard — {user.full_name}",
                             font=("Arial", 20, "bold"))
        label.pack(side="left", padx=20, pady=10)

        logout_btn = ctk.CTkButton(self.header_frame, text="Logout",
                                    command=parent.logout, width=80)
        logout_btn.pack(side="right", padx=20, pady=10)

        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_overview = self.tab_view.add("Overview")
        self.tab_invoices = self.tab_view.add("Invoices")
        self.tab_payments = self.tab_view.add("Payments")
        self.tab_reports = self.tab_view.add("Reports")

        self.setup_overview_tab()
        self.setup_invoices_tab()
        self.setup_payments_tab()
        self.setup_reports_tab()

    # ── Helpers ───────────────────────────────────────────────────────

    def _clear(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _badge(self, parent, text, color=None):
        if color is None:
            color = C.get(text, _GREY)
    def _embed_figure(self, parent, fig):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        return canvas

        f = ctk.CTkFrame(parent, fg_color=color, height=24, width=100)
        f.pack_propagate(False)
        f.pack(side="left", padx=5)
        ctk.CTkLabel(f, text=str(text).replace("_", " "), text_color="white",
                     font=("Arial", 11, "bold")).pack(expand=True)

    # ── Overview ──────────────────────────────────────────────────────

    def setup_overview_tab(self):
        frame = self.tab_overview
        self._clear(frame)

        # Stats
        try:
            stats = self.service.get_financial_stats()
        except Exception as e:
            ctk.CTkLabel(frame, text=f"Error loading stats: {e}").pack()
            return

        actions_frame = ctk.CTkFrame(frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(actions_frame, text="Generate Monthly Invoices",
                       command=self._generate_invoices, fg_color="#2ecc71", hover_color="#27ae60").pack(side="left", padx=5)
        ctk.CTkButton(actions_frame, text="Send Late Notifications",
                       command=self._send_notifications, fg_color="#e74c3c", hover_color="#c0392b").pack(side="left", padx=5)
        ctk.CTkButton(actions_frame, text="Refresh",
                       command=self.setup_overview_tab).pack(side="right", padx=5)

        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=10)

        items = [
            ("Collected Rent", f"£{stats['collected_total']:.2f}"),
            ("Pending Rent", f"£{stats['pending_total']:.2f}"),
            ("Maintenance Costs", f"£{stats['maintenance_total']:.2f}"),
            ("Overdue Invoices", str(stats['overdue_count'])),
        ]

        for idx, (title, value) in enumerate(items):
            card = ctk.CTkFrame(cards_frame)
            card.grid(row=0, column=idx, padx=8, pady=5, sticky="nsew")
            cards_frame.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold")).pack(pady=(0, 10))

        # Recent Payments Preview
        ctk.CTkLabel(frame, text="Recent Payments (Last 5)", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        payments = self.service.get_all_payments()[:5]
        
        if not payments:
            ctk.CTkLabel(frame, text="No recent payments recorded.").pack(padx=10, anchor="w")
        else:
            headers = ["Date", "Tenant", "Amount", "Method", "Unit"]
            hf = ctk.CTkFrame(frame)
            hf.pack(fill="x", padx=10)
            widths = [140, 180, 100, 120, 100]
            
            for i, h in enumerate(headers):
                ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"), width=widths[i], anchor="w").pack(side="left", padx=2)
            
            for p in payments:
                rf = ctk.CTkFrame(frame, height=40, fg_color=("gray85", "gray17"))
                rf.pack(fill="x", padx=10, pady=5)
                # Helper to vertically center labels
                rf.grid_columnconfigure((0,1,2,3,4), weight=1)
                
                ctk.CTkLabel(rf, text=_uk_date(p['paid_at']), width=widths[0], anchor="w").pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(rf, text=p['tenant_name'], width=widths[1], anchor="w").pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(rf, text=f"£{p['amount_paid']}", width=widths[2], anchor="w").pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(rf, text=str(p['method']).replace("_", " ").title(), width=widths[3], anchor="w").pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(rf, text=p['unit_code'], width=widths[4], anchor="w").pack(side="left", padx=10, pady=5)

    def _generate_invoices(self):
        try:
            count = self.service.generate_monthly_invoices()
            messagebox.showinfo("Invoices", f"Generated {count} new invoices for this month.")
            self.setup_overview_tab()
            self.setup_invoices_tab()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _send_notifications(self):
        try:
            count = self.service.send_late_notifications()
            messagebox.showinfo("Notifications", f"Sent notifications for {count} late invoices.")
            self.setup_overview_tab()
            self.setup_invoices_tab()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Invoices ──────────────────────────────────────────────────────

    def setup_invoices_tab(self):
        frame = self.tab_invoices
        self._clear(frame)

        filter_frame = ctk.CTkFrame(frame)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(filter_frame, text="Filter Status:").pack(side="left", padx=5)
        status_var = ctk.StringVar(value="All")
        
        def refresh(*args):
             self._populate_invoices(scroll_frame, status_var.get())

        ctk.CTkOptionMenu(filter_frame, variable=status_var, 
                           values=["All", "UNPAID", "LATE", "PAID"],
                           command=refresh).pack(side="left", padx=5)
        
        ctk.CTkButton(filter_frame, text="Refresh", command=lambda: refresh()).pack(side="right", padx=5)

        scroll_frame = ctk.CTkScrollableFrame(frame, label_text="Invoices")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initial load
        self.after(100, lambda: refresh())

    def _populate_invoices(self, parent, status_filter):
        self._clear(parent)
        
        s = None if status_filter == "All" else status_filter
        invoices = self.service.get_all_invoices(status=s)
        
        if not invoices:
            ctk.CTkLabel(parent, text="No invoices found.").pack(pady=20)
            return
            
        for inv in invoices:
            # Card Container
            row = ctk.CTkFrame(parent, border_width=0, corner_radius=8, fg_color=("gray85", "gray17"))
            row.pack(fill="x", pady=6, padx=5)
            
            # Left Info
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=15, pady=10, fill="x", expand=True)
            
            status_color = "#e74c3c" if inv['status'] == "LATE" else None
            line1 = f"Invoice #{inv['invoice_id']}  |  £{inv['amount']}  |  Due: {_uk_date(inv['due_date'])}"
            ctk.CTkLabel(info, text=line1, font=("Arial", 14, "bold"), text_color=status_color).pack(anchor="w")
            
            line2 = f"Tenant: {inv['tenant_name']} (NI: {inv['ni_number']})  |  Unit: {inv['unit_code']}"
            ctk.CTkLabel(info, text=line2, font=("Arial", 12), text_color="#bdc3c7").pack(anchor="w", pady=(2,0))
            
            # Badge
            self._badge(row, inv['status'])
            
            # Action (Pay)
            if inv['status'] in ('UNPAID', 'LATE'):
                ctk.CTkButton(row, text="Pay", width=80, 
                               command=lambda i=inv: self._record_payment_popup(i)).pack(side="right", padx=15, pady=10)

    def _record_payment_popup(self, inv):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Record Payment - Invoice #{inv['invoice_id']}")
        popup.geometry("350x250")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Record Payment for Invoice #{inv['invoice_id']}", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(popup, text=f"Total Due: £{inv['amount']}", font=("Arial", 12)).pack()

        entry = ctk.CTkEntry(popup, placeholder_text="Amount")
        entry.pack(pady=10, padx=20, fill="x")
        entry.insert(0, str(inv['amount']))
        
        method_var = ctk.StringVar(value="BANK_TRANSFER")
        ctk.CTkOptionMenu(popup, variable=method_var, 
                           values=["CASH", "CARD", "BANK_TRANSFER", "CHEQUE", "OTHER"]).pack(pady=5)
        
        def save():
            try:
                amt = float(entry.get())
                self.service.record_payment(inv['invoice_id'], amt, method_var.get())
                messagebox.showinfo("Success", "Payment recorded successfully", parent=popup)
                popup.destroy()
                self.setup_invoices_tab()
                self.setup_overview_tab() # Update stats
                self.setup_payments_tab() # Update payments
            except ValueError:
                messagebox.showerror("Error", "Invalid amount", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Save Payment", command=save).pack(pady=20)

    # ── Payments ──────────────────────────────────────────────────────

    def setup_payments_tab(self):
        frame = self.tab_payments
        self._clear(frame)
        
        ctk.CTkButton(frame, text="Refresh", 
                       command=self.setup_payments_tab).pack(anchor="ne", padx=10, pady=5)

        sf = ctk.CTkScrollableFrame(frame, label_text="Payment History")
        sf.pack(fill="both", expand=True, padx=10, pady=5)
        
        payments = self.service.get_all_payments()
        if not payments:
            ctk.CTkLabel(sf, text="No payments found.").pack(pady=20)
            return
            
        headers = ["ID", "Paid At", "Tenant", "Unit", "Method", "Amount"]
        widths = [60, 140, 180, 80, 120, 100]
        
        hf = ctk.CTkFrame(sf)
        hf.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(hf, text=h, font=("Arial", 12, "bold"), width=widths[i], anchor="w").pack(side="left", padx=4)
        
        for p in payments:
            rf = ctk.CTkFrame(sf)
            rf.pack(fill="x", pady=1)
            vals = [
                str(p['payment_id']),
                _uk_date(p['paid_at']),
                p['tenant_name'],
                p['unit_code'],
                p['method'],
                f"£{p['amount_paid']}"
            ]
            for i, v in enumerate(vals):
                 ctk.CTkLabel(rf, text=str(v).replace("_", " ").title(), width=widths[i], anchor="w").pack(side="left", padx=4)

    # ── Reports ───────────────────────────────────────────────────────

    def setup_reports_tab(self):
        frame = self.tab_reports
        self._clear(frame)

        grid = ctk.CTkFrame(frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)
        grid.grid_rowconfigure(0, weight=1)

        # 1. Collected vs Pending (Pie)
        stats = self.service.get_financial_stats()
        fig1 = Figure(figsize=(4, 3), dpi=100)
        ax1 = fig1.add_subplot(111)
        sizes = [stats['collected_total'], stats['pending_total']]
        labels = ['Collected', 'Pending']
        colors = ['#2ecc71', '#e74c3c']
        total_size = sum(sizes)
        if total_size > 0:
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        else:
            ax1.pie([1], labels=["No Data Available"], colors=["#e0e0e0"], startangle=90)
            ax1.set_title("Collected vs Pending Rent")
        
        c1 = ctk.CTkFrame(grid)
        c1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        canvas1 = self._embed_figure(c1, fig1)

        # 2. Maintenance Costs (Bar) - Monthly
        maint_data = self.service.get_maintenance_costs_data()
        fig2 = Figure(figsize=(4, 3), dpi=100)
        ax2 = fig2.add_subplot(111)
        
        months = [d['month'] for d in maint_data]
        costs = [float(d['total_cost']) for d in maint_data]
        
        if months:
            ax2.bar(months, costs, color='#3498db')
        else:
            ax2.text(0.5, 0.5, "No Data", ha='center', va='center')
            
        ax2.set_title("Maintenance Costs (Last 6 Months)")
        ax2.tick_params(axis='x', rotation=45)
        fig2.tight_layout()
        
        c2 = ctk.CTkFrame(grid)
        c2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        canvas2 = self._embed_figure(c2, fig2)

        # 3. Revenue Trend (Line)
        rev_data = self.service.get_revenue_data()
        fig3 = Figure(figsize=(4, 3), dpi=100)
        ax3 = fig3.add_subplot(111)
        
        months_r = [d['month'] for d in rev_data]
        total_r = [float(d['total_paid']) for d in rev_data]
        
        if months_r:
            ax3.plot(months_r, total_r, marker='o', color='#2ecc71')
        else:
             ax3.text(0.5, 0.5, "No Data", ha='center', va='center')
             
        ax3.set_title("Revenue Trend (Last 6 Months)")
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, linestyle='--', alpha=0.5)
        fig3.tight_layout()

        c3 = ctk.CTkFrame(grid)
        c3.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        canvas3 = self._embed_figure(c3, fig3)
