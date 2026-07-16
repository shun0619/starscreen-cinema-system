"""
Business Logic - Bookings  [Member 4]
Builds a Booking from real objects, previews the price breakdown, and
confirms it with payment (cash shows change due). Discounts are applied
automatically from the customer's tier -- staff never type a discount.
"""
import datetime

from data_access import booking_repository, customer_repository
from data_access import pricing_repository
from models.customer import Customer, GUEST
from models.booking import Booking
from models.payment import Payment, METHODS
from models.receipt import Receipt


def payment_methods():
    return METHODS


def make_guest():
    """An unregistered walk-in: Guest tier, no discount, no points."""
    return Customer("GUEST", "Guest (walk-in)", "", "", 0, GUEST)


def seat_price(screening, screening_seat):
    return pricing_repository.price_for(screening.screening_type,
                                        screening_seat.seat.seat_type)


def price_preview(customer, screening, selected_keys):
    """The full breakdown shown BEFORE payment is confirmed (assignment rule).
    Uses a temporary Booking so preview and final math can never disagree."""
    seats = [screening.seat_map[k] for k in selected_keys]
    temp = Booking("PREVIEW", customer, screening, seats, None,
                   pricing_repository.price_for)
    temp.calculate_total()
    return {
        "subtotal": temp.subtotal,
        "discount": temp.discount_amount,
        "gst": temp.gst_amount,
        "total": temp.final_amount,
        "tier": customer.get_membership_tier(),
    }


def confirm_booking(current_user, customer, screening, selected_keys,
                    payment_method, cash_tendered_text=""):
    """Validates everything, reserves the seats, takes payment, and
    returns (booking, payment, receipt_text). Raises ValueError with a
    clear message on any problem -- the UI shows it, never crashes."""
    if screening is None:
        raise ValueError("Please choose a screening.")
    if customer is None:
        raise ValueError("Please look up a customer (or select Guest).")
    if not selected_keys:
        raise ValueError("Please select at least one seat.")

    cash_tendered = None
    if payment_method == "Cash":
        try:
            cash_tendered = float(cash_tendered_text)
        except (TypeError, ValueError):
            raise ValueError("Please enter a valid cash amount, e.g. 50.00")

    seats = [screening.seat_map[k] for k in selected_keys]
    booking = Booking(booking_repository.next_id(), customer, screening,
                      seats, current_user, pricing_repository.price_for)

    # The staff member processes the booking (Cashier/Manager both can).
    old_tier, new_tier = current_user.book_ticket(booking)

    payment = Payment(booking_repository.next_payment_id(), booking,
                      payment_method, cash_tendered)
    payment.process_payment()

    # Payment succeeded -- now record everything.
    if old_tier is not new_tier:
        customer_repository.add_history(customer, old_tier.tier_name,
                                        new_tier.tier_name,
                                        datetime.date.today().isoformat())
    booking_repository.add(booking)
    booking_repository.add_payment(payment)

    receipt = Receipt(f"RC-{booking.booking_id}", booking, payment)
    # Write the whole booking to SQL Server in one transaction
    # (seat flags, customer points/tier, payment, and receipt included).
    booking_repository.persist_confirmed(booking, payment, receipt.receipt_id)
    return booking, payment, receipt.generate_receipt()


def list_recent_bookings(limit=8):
    return booking_repository.get_all()[:limit]


def booking_history_for(customer):
    return [b for b in booking_repository.get_all() if b.customer is customer]


def total_revenue():
    return round(sum(b.final_amount for b in booking_repository.get_all()), 2)
