"""
==========================================
Domain Model - Seat & ScreeningSeat  [Member 4]
==========================================
A Seat is a physical chair in a Screen (row + number + type).
A ScreeningSeat is that chair *for one particular screening* -- the same
chair can be free at 2pm and booked at 7pm, so availability lives here,
not on the Seat itself.
"""


class Seat:

    def __init__(self, seat_id, row, number, seat_type="Standard"):
        self.seat_id = seat_id
        self.row = row                  # "A".."E"
        self.number = number            # 1..10
        self.seat_type = seat_type      # "Standard" or "Premium"

    @property
    def seat_number(self):
        return f"{self.row}{self.number}"

    @property
    def is_premium(self):
        return self.seat_type == "Premium"


class ScreeningSeat:
    """One seat's availability within one screening."""

    def __init__(self, screening_seat_id, seat, is_booked=False):
        self.screening_seat_id = screening_seat_id
        self.seat = seat
        self.is_booked = is_booked

    def reserve(self):
        """Returns False if the seat was already taken (no double booking)."""
        if self.is_booked:
            return False
        self.is_booked = True
        return True

    def release(self):
        self.is_booked = False
