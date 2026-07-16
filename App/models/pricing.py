"""
==========================================
Domain Model - Pricing  [Member 4]
==========================================
Ticket prices depend on BOTH the screening type and the seat type
(assignment rule). This is a lookup table, so prices are data -- not
hard-coded inside the booking calculation.
"""


class Pricing:

    def __init__(self, pricing_id, screening_type, seat_type, base_price):
        self.pricing_id = pricing_id
        self.screening_type = screening_type
        self.seat_type = seat_type
        self.base_price = base_price

    def matches(self, screening_type, seat_type):
        return self.screening_type == screening_type and self.seat_type == seat_type
