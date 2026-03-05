import customtkinter as ctk
from models import User
from services.tenant_service import TenantService
from typing import TYPE_CHECKING
from tkinter import messagebox

if TYPE_CHECKING:
    from views.gui import App

class TenantDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.user = user
        self.service = TenantService(user.tenant_id)
        self.details = self.service.get_tenant_details() # Fetch tenant specific details like NI number

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Tabview

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        label = ctk.CTkLabel(self.header_frame, text=f"Welcome, {user.full_name}", font=("Arial", 20, "bold"))
        label.pack(side="left", padx=20, pady=10)

        logout_btn = ctk.CTkButton(self.header_frame, text="Logout", command=parent.logout, width=80)
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
        
        # Check for overdue payments after loading UI
        self.after(500, self.check_overdue_payments)

    def check_overdue_payments(self):
        overdue = self.service.get_unpaid_invoices(overdue_only=True)
        if overdue:
            count = len(overdue)
            total_amount = sum(float(inv['amount_due']) for inv in overdue)
            messagebox.showwarning(
                "Overdue Payments Alert",
                f"Attention: You have {count} overdue invoice(s) totaling £{total_amount:.2f}.\n"
                "Please check the Payments tab to settle these immediately."
            )

    def setup_overview_tab(self):
        frame = self.tab_overview
        
        # Clear existing widgets to prevent duplication on refresh
        for widget in frame.winfo_children():
            widget.destroy()
        
        info_text = f"""
        Name: {self.user.full_name}
        Email: {self.user.email}
        NI Number: {self.details.get('ni_number', 'N/A')}
        Occupation: {self.details.get('occupation', 'N/A')}
        """
        ctk.CTkLabel(frame, text="Your Information", font=("Arial", 16, "bold")).pack(pady=10, anchor="w")
        ctk.CTkLabel(frame, text=info_text, justify="left").pack(pady=5, anchor="w")

        # Quick Stats or Alerts could go here
        unpaid = self.service.get_unpaid_invoices()
        if unpaid:
            alert_frame = ctk.CTkFrame(frame, fg_color="red")
            alert_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(alert_frame, text=f"You have {len(unpaid)} unpaid invoice(s)!", text_color="white").pack(pady=5)

    def setup_payments_tab(self):
        frame = self.tab_payments

        # Clear existing widgets to prevent duplication on refresh
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Action Buttons
        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", pady=5)
        # Placeholder for Make Payment
        ctk.CTkButton(actions, text="Make Payment", command=self.make_payment_popup).pack(side="left", padx=5)
        # Placeholder for Graph
        ctk.CTkButton(actions, text="View Payment Graph", command=lambda: messagebox.showinfo("Info", "Graph feature WIP")).pack(side="left", padx=5)

        # History List
        history_frame = ctk.CTkScrollableFrame(frame, label_text="Payment History")
        history_frame.pack(fill="both", expand=True, pady=10)

        payments = self.service.get_payment_history()
        
        if not payments:
            ctk.CTkLabel(history_frame, text="No payment history found.").pack(pady=20)
        else:
            # Header Row
            headers = ["Date", "Amount", "Method", "Due Date"]
            header_frame = ctk.CTkFrame(history_frame)
            header_frame.pack(fill="x")
            for i, h in enumerate(headers):
                ctk.CTkLabel(header_frame, text=h, font=("Arial", 12, "bold"), width=100).pack(side="left", padx=5)

            # Data Rows
            for p in payments:
                row = ctk.CTkFrame(history_frame)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=str(p['paid_at']), width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"£{p['amount_paid']}", width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=p['method'], width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=str(p['due_date']), width=100).pack(side="left", padx=5)

    def setup_maintenance_tab(self):
        frame = self.tab_maintenance
        
        # Input for new request
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(input_frame, text="New Request:").pack(side="left", padx=5)
        self.mnt_desc = ctk.CTkEntry(input_frame, placeholder_text="Description", width=300)
        self.mnt_desc.pack(side="left", padx=5)
        
        self.mnt_priority = ctk.CTkOptionMenu(input_frame, values=["Low", "Medium", "High"])
        self.mnt_priority.set("Medium")
        self.mnt_priority.pack(side="left", padx=5)

        # Apartment selector if multiple
        self.active_leases = self.service.get_active_lease_info()
        self.lease_options = {f"{l['unit_code']} ({l['city']})": l['apartment_id'] for l in self.active_leases}
        
        if len(self.lease_options) > 1:
            self.lease_selector = ctk.CTkComboBox(input_frame, values=list(self.lease_options.keys()))
            self.lease_selector.pack(side="left", padx=5)
        else:
            self.lease_selector = None

        ctk.CTkButton(input_frame, text="Submit", command=self.submit_maintenance).pack(side="left", padx=5)

        # List of existing requests
        list_frame = ctk.CTkScrollableFrame(frame, label_text="Your Requests")
        list_frame.pack(fill="both", expand=True, pady=5)
        
        requests = self.service.get_maintenance_requests()
        for req in requests:
            row_text = f"{req['date_created']} - {req['description']} [{req['status']}] (Priority: {req['priority']})"
            ctk.CTkLabel(list_frame, text=row_text, anchor="w").pack(fill="x", padx=5, pady=2)
            # Add progress bar or detailed view button here if needed

    def setup_complaints_tab(self):
        frame = self.tab_complaints
        
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", pady=10)

        self.comp_desc = ctk.CTkEntry(input_frame, placeholder_text="Describe your complaint...", width=400)
        self.comp_desc.pack(side="left", padx=5)
        ctk.CTkButton(input_frame, text="Submit", command=self.submit_complaint).pack(side="left", padx=5)
        
        ctk.CTkLabel(frame, text="Previous complaints go here...").pack(pady=20)

    def submit_maintenance(self):
        desc = self.mnt_desc.get()
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
            messagebox.showinfo("Success", "Request Submitted")
            self.mnt_desc.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Failed to submit request.")

    def submit_complaint(self):
        desc = self.comp_desc.get()
        if not desc:
            return
        if self.service.submit_complaint(desc):
             messagebox.showinfo("Success", "Complaint Submitted")
             self.comp_desc.delete(0, 'end')
        else:
             messagebox.showerror("Error", "Could not submit complaint. active lease?")

    def make_payment_popup(self):
        unpaid_invoices = self.service.get_unpaid_invoices()
        if not unpaid_invoices:
            messagebox.showinfo("Info", "You have no unpaid invoices.")
            return

        # Create a custom popup window
        popup = ctk.CTkToplevel(self)
        popup.title("Make Payment")
        popup.geometry("400x300")
        
        # Make the popup modal
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Select Invoice to Pay:", font=("Arial", 14, "bold")).pack(pady=10)

        # Invoice Selection
        invoice_options = {f"Inv #{i['invoice_id']} - £{i['amount_due']} (Due: {i['due_date']})": i for i in unpaid_invoices}
        selected_invoice = ctk.StringVar(value=list(invoice_options.keys())[0])
        dropdown = ctk.CTkOptionMenu(popup, variable=selected_invoice, values=list(invoice_options.keys()))
        dropdown.pack(pady=5)

        ctk.CTkLabel(popup, text="Card Number (16 digits):").pack(pady=(15, 5))
        card_entry = ctk.CTkEntry(popup, placeholder_text="XXXX XXXX XXXX XXXX")
        card_entry.pack(pady=5)

        def process_payment():
            key = selected_invoice.get()
            inv_data = invoice_options[key]
            card_num = card_entry.get().replace(" ", "")

            # Validation
            if not card_num.isdigit() or len(card_num) != 16:
                messagebox.showerror("Error", "Invalid Card Number. Must be 16 digits.", parent=popup)
                return
            
            # Process
            success = self.service.pay_invoice(inv_data['invoice_id'], float(inv_data['amount_due']))
            if success:
                messagebox.showinfo("Success", "Payment Successful!", parent=popup)
                popup.destroy()
                # Refresh UI
                self.setup_payments_tab() 
                self.setup_overview_tab() # Refresh alerts
            else:
                messagebox.showerror("Error", "Payment failed.", parent=popup)

        ctk.CTkButton(popup, text="Pay Now", command=process_payment).pack(pady=20)