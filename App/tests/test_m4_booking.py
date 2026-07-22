"""
M4 - Booking, payment & receipt.

TC-04: price = subtotal - tier discount + 15% GST. Two $10 standard seats
for a Silver member (20% off): 20 - 4 = 16, +15% GST = 18.40.
"""

from models.customer import Customer, SILVER
from models.seat import Seat, ScreeningSeat
from models.booking import Booking


def test_booking_price_breakdown():
    customer = Customer("CU-TEST", "Silver Member", "", "s@example.com", 600, SILVER)
    seats = [
        ScreeningSeat("SS-1", Seat("S1", "C", 1, "Standard")),
        ScreeningSeat("SS-2", Seat("S2", "C", 2, "Standard")),
    ]

    class _Screening:  # calculate_total() only reads screening_type
        screening_type = "Standard"

    booking = Booking("BK-TEST", customer, _Screening(), seats, None,
                      price_lookup=lambda screening_type, seat_type: 10.00)
    booking.calculate_total()

    assert booking.subtotal == 20.00
    assert booking.discount_amount == 4.00
    assert booking.gst_amount == 2.40
    assert booking.final_amount == 18.40
