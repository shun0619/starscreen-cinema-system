"""
Data Access - Bookings & payments  [M4]
Reads come from the in-memory objects (loaded from SQL Server or the
sample data). A confirmed booking is written to the database as ONE
transaction (booking + seats + payment + receipt + customer update),
so the database can never end up half-saved.
"""
from data.store import BOOKINGS, PAYMENTS
from data_access import db


def get_all():
    return BOOKINGS


def add(booking):
    BOOKINGS.insert(0, booking)  # newest first


def next_id():
    return f"BK-{len(BOOKINGS) + 1001}"


def add_payment(payment):
    PAYMENTS.append(payment)


def next_payment_id():
    return f"PAY-{len(PAYMENTS) + 1001}"


def persist_confirmed(booking, payment, receipt_id):
    """Write a completed booking through to SQL Server in a single
    transaction. No-op when the database is disabled."""
    if not db.enabled():
        return

    customer_id = (booking.customer.customer_id
                   if booking.customer.customer_id != "GUEST" else None)
    statements = [(
        "INSERT INTO BOOKING (booking_id, customer_id, staff_id, "
        "booking_date, subtotal, discount_amount, gst_amount, final_amount, "
        "points_earned) VALUES (?, ?, ?, GETDATE(), ?, ?, ?, ?, ?)",
        (booking.booking_id, customer_id, booking.staff.staff_id,
         booking.subtotal, booking.discount_amount, booking.gst_amount,
         booking.final_amount, booking.points_earned),
    )]

    for booking_seat in booking.booking_seats:
        statements.append((
            "INSERT INTO BOOKING_SEAT (booking_seat_id, booking_id, "
            "screening_seat_id) VALUES (?, ?, ?)",
            (booking_seat.booking_seat_id, booking.booking_id,
             booking_seat.screening_seat.screening_seat_id),
        ))
        statements.append((
            "UPDATE SCREENING_SEAT SET is_booked = 1 "
            "WHERE screening_seat_id = ?",
            (booking_seat.screening_seat.screening_seat_id,),
        ))

    if customer_id:  # guests earn no points and are not stored
        statements.append((
            "UPDATE CUSTOMER SET points = ?, tier_id = ? "
            "WHERE customer_id = ?",
            (booking.customer.points, booking.customer.tier.tier_id,
             customer_id),
        ))

    statements.append((
        "INSERT INTO PAYMENT (payment_id, booking_id, payment_method, "
        "amount, payment_date) VALUES (?, ?, ?, ?, GETDATE())",
        (payment.payment_id, booking.booking_id, payment.payment_method,
         payment.amount),
    ))
    statements.append((
        "INSERT INTO RECEIPT (receipt_id, booking_id, issued_at) "
        "VALUES (?, ?, GETDATE())",
        (receipt_id, booking.booking_id),
    ))

    db.execute_transaction(statements)
