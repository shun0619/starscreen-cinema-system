"""
==========================================
Domain Model - Payment  [Member 4]
==========================================
Cash, Card, and Voucher are supported. Cash payments must show the
change due (assignment rule).
"""

METHODS = ["Cash", "Card", "Voucher"]


class Payment:

    def __init__(self, payment_id, booking, payment_method, cash_tendered=None):
        self.payment_id = payment_id
        self.booking = booking
        self.payment_method = payment_method
        self.amount = booking.final_amount
        self.cash_tendered = cash_tendered
        self.change_due = 0.0
        self.is_processed = False

    def process_payment(self):
        """Validates cash amounts and computes change. Raises ValueError
        on bad input so the UI can show a clear message (never crash)."""
        if self.payment_method not in METHODS:
            raise ValueError("Please choose a payment method.")
        if self.payment_method == "Cash":
            if self.cash_tendered is None:
                raise ValueError("Please enter the cash amount received.")
            if self.cash_tendered < self.amount:
                raise ValueError(
                    f"Cash received (${self.cash_tendered:.2f}) is less than "
                    f"the total (${self.amount:.2f}).")
            self.change_due = round(self.cash_tendered - self.amount, 2)
        self.is_processed = True
        return self.change_due
