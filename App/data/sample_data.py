"""
==========================================
Sample data (stand-in for the real database)  [Member 5]
==========================================
Builds the app's starting data as real objects from models/.
When the team connects SQL Server later, ONLY data_access/ (and this
file) changes -- models, business_logic, and screens stay the same.

The seed bookings at the bottom are created through the real
Booking.confirm_booking() flow, so seats are genuinely reserved and
loyalty points/tiers are genuinely updated -- which makes the discount
and reporting logic demonstrable, as the assignment requires.
"""

import datetime

frommodels.staff import Cashier, Manager
frommodels.customer import Customer, REGULAR, SILVER, GOLD, tier_for_points
frommodels.movie import Movie
frommodels.seat import Seat
frommodels.screening import Screen, Screening
frommodels.pricing import Pricing
frommodels.booking import Booking
frommodels.payment import Payment

TODAY = datetime.date.today().isoformat()

# ---- Staff logins -------------------------------------------
USERS = {
    "cashier": Cashier("ST-01", "cashier", "cashier123", "Alex Kim"),
    "manager": Manager("ST-02", "manager", "manager123", "John Reynolds"),
}

# ---- Movies (genres fixed by the brief) ----------------------
GENRES = ["All", "Action", "Drama", "Horror", "Kids", "Romance", "Thriller"]

MOVIES = [
    Movie("MV-01", "Dune: Part Three", "Action", 155, "PG-13"),
    Movie("MV-02", "Midnight in Paris", "Romance", 114, "PG"),
    Movie("MV-03", "Quantum Breach", "Thriller", 125, "MA15+"),
    Movie("MV-04", "The Haunting Hour", "Horror", 108, "R16"),
    Movie("MV-05", "Dragon's Fury", "Kids", 105, "G"),
    Movie("MV-06", "Ocean's Story", "Drama", 118, "PG", is_active=False),
]


def _movie(title):
    return next(m for m in MOVIES if m.title == title)


# ---- Screens (3 physical screens, rows A-E x seats 1-10) -----
# Rows A and B are Premium seating; C-E are Standard.
SEAT_ROWS = ["A", "B", "C", "D", "E"]
SEAT_COLUMNS = list(range(1, 11))
PREMIUM_ROWS = {"A", "B"}


def _build_seats(screen_number):
    seats = []
    for row in SEAT_ROWS:
        for number in SEAT_COLUMNS:
            seat_type = "Premium" if row in PREMIUM_ROWS else "Standard"
            seats.append(Seat(f"S{screen_number}-{row}{number}", row, number, seat_type))
    return seats


SCREENS = [Screen(f"SCR-{n}", n, _build_seats(n)) for n in (1, 2, 3)]


# ---- Pricing lookup (screening type x seat type) --------------
PRICING = [
    Pricing("PR-01", "Standard", "Standard", 15.00),
    Pricing("PR-02", "Standard", "Premium", 22.00),
    Pricing("PR-03", "IMAX", "Standard", 22.00),
    Pricing("PR-04", "IMAX", "Premium", 30.00),
    Pricing("PR-05", "Kids", "Standard", 10.00),
    Pricing("PR-06", "Kids", "Premium", 14.00),
]

SCREENING_TYPES = ["Standard", "IMAX", "Kids"]


def get_price(screening_type, seat_type):
    for p in PRICING:
        if p.matches(screening_type, seat_type):
            return p.base_price
    return 15.00  # safe fallback so the app never crashes on a missing row


# ---- Screenings (each owns its own seat availability map) -----
def _scatter(screening_index):
    """A deterministic sprinkle of pre-booked seats, different per screening."""
    taken = set()
    for i, row in enumerate(SEAT_ROWS):
        for col in SEAT_COLUMNS:
            if (i * 7 + col * 3 + screening_index * 5) % 9 == 0:
                taken.add((row, col))
    return taken


SCREENINGS = [
    Screening("SC-01", _movie("Dune: Part Three"), SCREENS[0], TODAY, "10:00 AM", "IMAX", _scatter(1)),
    Screening("SC-02", _movie("Dune: Part Three"), SCREENS[0], TODAY, "7:00 PM", "IMAX", _scatter(2)),
    Screening("SC-03", _movie("Midnight in Paris"), SCREENS[1], TODAY, "2:00 PM", "Standard", _scatter(3)),
    Screening("SC-04", _movie("Quantum Breach"), SCREENS[1], TODAY, "8:30 PM", "Standard", _scatter(4)),
    Screening("SC-05", _movie("The Haunting Hour"), SCREENS[2], TODAY, "9:00 PM", "Standard", _scatter(5)),
    Screening("SC-06", _movie("Dragon's Fury"), SCREENS[2], TODAY, "11:00 AM", "Kids", _scatter(6)),
]


# ---- Customers (one from each registered tier, per the brief) --
def _customer(cid, name, phone, email, points):
    return Customer(cid, name, phone, email, points, tier_for_points(points))


CUSTOMERS = [
    _customer("CU-0001", "Sarah Johnson", "0412 345 678", "sarah.j@email.com", 620),
    _customer("CU-0002", "Michael Chen", "0423 456 789", "m.chen@email.com", 1450),
    _customer("CU-0003", "Emma Williams", "0434 567 890", "emma.w@email.com", 180),
    _customer("CU-0004", "James Rodriguez", "0445 678 901", "j.rod@email.com", 40),
    _customer("CU-0005", "Lisa Thompson", "0456 789 012", "lisa.t@email.com", 980),
]

# Tier change log: (customer, old tier name, new tier name, when)
MEMBERSHIP_HISTORY = []

# ---- Seed bookings (run through the REAL booking flow) --------
BOOKINGS = []
PAYMENTS = []


def _seed_booking(customer, screening, seat_keys, method="Card"):
    seats = [screening.seat_map[k] for k in seat_keys if not screening.seat_map[k].is_booked]
    if not seats:
        return
    booking = Booking(f"BK-{len(BOOKINGS) + 1001}", customer, screening, seats,
                      USERS["cashier"], get_price)
    old_tier, new_tier = booking.confirm_booking()
    if old_tier is not new_tier:
        MEMBERSHIP_HISTORY.append((customer, old_tier.tier_name, new_tier.tier_name, TODAY))
    payment = Payment(f"PAY-{len(PAYMENTS) + 1001}", booking, method,
                      cash_tendered=booking.final_amount if method == "Cash" else None)
    payment.process_payment()
    BOOKINGS.insert(0, booking)
    PAYMENTS.append(payment)


_seed_booking(CUSTOMERS[1], SCREENINGS[1], [("A", 4), ("A", 5)])          # Gold, IMAX premium
_seed_booking(CUSTOMERS[0], SCREENINGS[2], [("C", 3), ("C", 4)], "Cash")  # Silver, standard
_seed_booking(CUSTOMERS[4], SCREENINGS[3], [("B", 6)])                    # Silver->near Gold
_seed_booking(CUSTOMERS[2], SCREENINGS[5], [("D", 2), ("D", 3), ("D", 4)])  # Regular, kids
_seed_booking(CUSTOMERS[3], SCREENINGS[4], [("E", 7)])                    # Regular, horror
