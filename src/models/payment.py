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
    
    def get_payment_id(self) -> int:
        return self.payment_id
    
    def get_invoice(self) -> Invoice:
        return self.invoice
    
    def get_date_paid(self) -> float:
        return self.date_paid
    
    def get_amount_paid(self) -> float:
        return self.amount_paid
    
    def get_payment_method(self) -> str:
        return self.payment_method
    
    def get_recorded_by(self) -> Staff:
        return self.recorded_by
    
    def set_payment_id(self, payment_id: int) -> None:
        self.payment_id = payment_id
        
    def set_invoice(self, invoice: Invoice) -> None:
        self.invoice = invoice
        
    def set_date_paid(self, date_paid: float) -> None:
        self.date_paid = date_paid
        
    def set_amount_paid(self, amount_paid: float) -> None:
        self.amount_paid = amount_paid
        
    def set_payment_method(self, payment_method: str) -> None:
        self.payment_method = payment_method
        
    def set_recorded_by(self, recorded_by: Staff) -> None:
        self.recorded_by = recorded_by