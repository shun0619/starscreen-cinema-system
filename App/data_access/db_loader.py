"""
==========================================
Data Access - DB loader  [M5]
==========================================
Rebuilds the SAME model objects sample_data.py builds, but from the
SQL Server rows created by database/schema.sql. It is imported only
when db.enabled() is True (see store.py), loads everything once
at startup, and the repositories then work on these objects exactly
as they do with sample data. Changes are written back to the database
by the repositories' persist functions (write-through).
"""

from database import db
from models.staff import Cashier, Manager
from models.customer import Customer, TIERS, GUEST
from models.movie import Movie
from models.seat import Seat
from models.screening import Screen, Screening
from models.pricing import Pricing
from models.booking import Booking
from models.payment import Payment

GENRES = ["All", "Action", "Drama", "Horror", "Kids", "Romance", "Thriller"]
SCREENING_TYPES = ["Standard", "IMAX", "Kids"]

# DB tier rows map onto the module-level tier constants so identity
# checks (e.g. "tier is not GUEST") keep working.
_TIER_BY_ID = {t.tier_id: t for t in TIERS}


def _seat_key(seat_number):
    """'A5' -> ('A', 5), the key used by Screening.seat_map."""
    return seat_number[0], int(seat_number[1:])


# ---- Staff [M1] ----------------------------------------------
USERS = {}
for row in db.query("SELECT staff_id, username, password, full_name, role "
                    "FROM STAFF"):
    staff_class = Manager if row.role == "Manager" else Cashier
    USERS[row.username] = staff_class(row.staff_id, row.username,
                                      row.password, row.full_name)
_STAFF_BY_ID = {u.staff_id: u for u in USERS.values()}

# ---- Movies [M3] ---------------------------------------------
MOVIES = [
    Movie(r.movie_id, r.title, r.genre, r.duration_min, r.rating or "",
          bool(r.is_active))
    for r in db.query("SELECT movie_id, title, genre, duration_min, rating, "
                      "is_active FROM MOVIE ORDER BY movie_id")
]
_MOVIE_BY_ID = {m.movie_id: m for m in MOVIES}

# ---- Screens & seats [M3/M4] ---------------------------------
SCREENS = []
_SCREEN_BY_ID = {}
for r in db.query("SELECT screen_id, screen_number FROM SCREEN "
                  "ORDER BY screen_number"):
    seats = []
    for s in db.query("SELECT seat_id, seat_number, seat_type FROM SEAT "
                      "WHERE screen_id = ?", (r.screen_id,)):
        seat_row, seat_no = _seat_key(s.seat_number)
        seats.append(Seat(s.seat_id, seat_row, seat_no, s.seat_type))
    seats.sort(key=lambda seat: (seat.row, seat.number))
    screen = Screen(r.screen_id, r.screen_number, seats)
    SCREENS.append(screen)
    _SCREEN_BY_ID[r.screen_id] = screen

# ---- Pricing [M4] --------------------------------------------
PRICING = [
    Pricing(r.pricing_id, r.screening_type, r.seat_type, float(r.base_price))
    for r in db.query("SELECT pricing_id, screening_type, seat_type, "
                      "base_price FROM PRICING")
]


def get_price(screening_type, seat_type):
    for pricing in PRICING:
        if pricing.matches(screening_type, seat_type):
            return pricing.base_price
    return 15.00  # safe fallback so the app never crashes on a missing row


# ---- Screenings + which seats are already booked [M3/M4] -----
SCREENINGS = []
_SCREENING_BY_ID = {}
for r in db.query("SELECT screening_id, movie_id, screen_id, "
                  "CONVERT(varchar(10), screening_date, 23) AS d, "
                  "screening_time, screening_type "
                  "FROM SCREENING ORDER BY screening_id"):
    booked = {
        _seat_key(b.seat_number)
        for b in db.query(
            "SELECT s.seat_number FROM SCREENING_SEAT ss "
            "JOIN SEAT s ON s.seat_id = ss.seat_id "
            "WHERE ss.screening_id = ? AND ss.is_booked = 1",
            (r.screening_id,))
    }
    screening = Screening(r.screening_id, _MOVIE_BY_ID[r.movie_id],
                          _SCREEN_BY_ID[r.screen_id], r.d, r.screening_time,
                          r.screening_type, booked)
    SCREENINGS.append(screening)
    _SCREENING_BY_ID[r.screening_id] = screening

# ---- Customers & membership history [M2] ---------------------
CUSTOMERS = [
    Customer(r.customer_id, r.name, r.phone or "", r.email, r.points,
             _TIER_BY_ID.get(r.tier_id, GUEST))
    for r in db.query("SELECT customer_id, name, phone, email, points, "
                      "tier_id FROM CUSTOMER ORDER BY customer_id")
]
_CUSTOMER_BY_ID = {c.customer_id: c for c in CUSTOMERS}

MEMBERSHIP_HISTORY = [
    (_CUSTOMER_BY_ID[r.customer_id],
     _TIER_BY_ID[r.old_tier_id].tier_name,
     _TIER_BY_ID[r.new_tier_id].tier_name,
     r.changed_at)
    for r in db.query("SELECT customer_id, old_tier_id, new_tier_id, "
                      "CONVERT(varchar(10), changed_at, 23) AS changed_at "
                      "FROM MEMBERSHIP_HISTORY ORDER BY history_id")
    if r.customer_id in _CUSTOMER_BY_ID
]

# ---- Bookings & payments [M4] --------------------------------
BOOKINGS = []
PAYMENTS = []
_BOOKING_BY_ID = {}

for r in db.query("SELECT booking_id, customer_id, staff_id, "
                  "CONVERT(varchar(10), booking_date, 23) AS d, "
                  "subtotal, discount_amount, gst_amount, final_amount, "
                  "points_earned FROM BOOKING ORDER BY booking_id"):
    seat_rows = db.query(
        "SELECT ss.screening_id, s.seat_number FROM BOOKING_SEAT bs "
        "JOIN SCREENING_SEAT ss ON ss.screening_seat_id = bs.screening_seat_id "
        "JOIN SEAT s ON s.seat_id = ss.seat_id "
        "WHERE bs.booking_id = ? ORDER BY bs.booking_seat_id",
        (r.booking_id,))
    if not seat_rows:
        continue
    screening = _SCREENING_BY_ID[seat_rows[0].screening_id]
    screening_seats = [screening.seat_map[_seat_key(sr.seat_number)]
                       for sr in seat_rows]
    customer = (_CUSTOMER_BY_ID.get(r.customer_id)
                or Customer("GUEST", "Guest (walk-in)", "", "", 0, GUEST))
    staff = _STAFF_BY_ID.get(r.staff_id)

    booking = Booking(r.booking_id, customer, screening, screening_seats,
                      staff, get_price)
    # Restore the confirmed state exactly as it was saved (no re-reserving,
    # no re-awarding points -- that all happened when it was first made).
    booking.booking_date = r.d
    booking.subtotal = float(r.subtotal)
    booking.discount_amount = float(r.discount_amount)
    booking.gst_amount = float(r.gst_amount)
    booking.final_amount = float(r.final_amount)
    booking.points_earned = r.points_earned or 0
    booking.is_confirmed = True
    BOOKINGS.insert(0, booking)  # newest first, same as sample data
    _BOOKING_BY_ID[r.booking_id] = booking

for r in db.query("SELECT payment_id, booking_id, payment_method "
                  "FROM PAYMENT ORDER BY payment_id"):
    booking = _BOOKING_BY_ID.get(r.booking_id)
    if booking is None:
        continue
    payment = Payment(r.payment_id, booking, r.payment_method)
    payment.is_processed = True
    PAYMENTS.append(payment)

print(f"[db] Loaded {len(MOVIES)} movies, {len(SCREENINGS)} screenings, "
      f"{len(CUSTOMERS)} customers, {len(BOOKINGS)} bookings from SQL Server.")
