from .invoice import Invoice
from .staff import Staff

class Payment:
    def __init__(self, payment_id: int, invoice: Invoice, date_paid: float, amount_paid: float, payment_method: str, recorded_by: Staff) -> None:
        self.payment_id = payment_id
        self.invoice = invoice
        self.date_paid = date_paid
        self.amount_paid = amount_paid
        self.payment_method = payment_method
        self.recorded_by = recorded_by