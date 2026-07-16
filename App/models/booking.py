"""
==========================================
Domain Model - Booking  [Member 4]
==========================================
Price rule (from the assignment brief):
  subtotal   = sum of each seat's base price (by seat type x screening type)
  discount   = membership tier % of the subtotal   (applied automatically)
  gst        = 15% of (subtotal - discount)
  final      = subtotal - discount + gst
"""

import datetime
import config


class BookingSeat:
    """One booked seat inside a Booking -- the link between the Booking
    and the exact ScreeningSeat that was reserved. Matches the
    BOOKING_SEAT table in the ER diagram: its UNIQUE screening_seat_id
    is what prevents double booking at the database level."""

    def __init__(self, booking_seat_id, screening_seat):
        self.booking_seat_id = booking_seat_id
        self.screening_seat = screening_seat  # ScreeningSeat instance


class Booking:

    def __init__(self, booking_id, customer, screening, screening_seats, staff,
                 price_lookup):
        self.booking_id = booking_id
        self.customer = customer            # Customer instance
        self.screening = screening          # Screening instance
        # One BookingSeat per selected ScreeningSeat (matches the class/ER diagrams)
        self.booking_seats = [
            BookingSeat(f"{booking_id}-{i}", ss)
            for i, ss in enumerate(screening_seats, start=1)
        ]
        self.staff = staff                  # Staff member who processed it
        self.price_lookup = price_lookup    # function(screening_type, seat_type) -> price
        self.booking_date = datetime.date.today().isoformat()

        self.subtotal = 0.0
        self.discount_amount = 0.0
        self.gst_amount = 0.0
        self.final_amount = 0.0
        self.points_earned = 0
        self.is_confirmed = False

    @property
    def screening_seats(self):
        """The reserved ScreeningSeat objects (read via the BookingSeat
        links, so receipts/reports don't need to know about the join)."""
        return [bs.screening_seat for bs in self.booking_seats]

    def calculate_total(self):
        """Fills in the full price breakdown and returns final_amount."""
        self.subtotal = sum(
            self.price_lookup(self.screening.screening_type, ss.seat.seat_type)
            for ss in self.screening_seats
        )
        self.discount_amount = self.customer.tier.calculate_discount(self.subtotal)
        after_discount = self.subtotal - self.discount_amount
        self.gst_amount = round(after_discount * config.GST_PERCENT / 100, 2)
        self.final_amount = round(after_discount + self.gst_amount, 2)
        return self.final_amount

    def confirm_booking(self):
        """Reserves every seat (rejecting double-booking), locks in the
        price, and awards loyalty points -- which may auto-upgrade the
        customer's tier. Returns (old_tier, new_tier)."""
        for ss in self.screening_seats:
            if not ss.reserve():
                raise ValueError(f"Seat {ss.seat.seat_number} has just been taken.")
        self.calculate_total()
        old_points = self.customer.points
        old_tier, new_tier = self.customer.update_points(self.final_amount)
        self.points_earned = self.customer.points - old_points
        self.is_confirmed = True
        return old_tier, new_tier
