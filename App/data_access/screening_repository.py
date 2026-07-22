"""
Data Access - Screens & screenings  [M3]
Reads come from the in-memory objects (loaded from SQL Server or the
sample data). Every change is also written through to the database
when it is enabled -- the persist functions are no-ops otherwise.
"""
from store import SCREENS, SCREENINGS, SCREENING_TYPES
from database import db


def get_all():
    return SCREENINGS


def get_screens():
    return SCREENS


def get_screening_types():
    return SCREENING_TYPES


def add(screening):
    SCREENINGS.append(screening)
    if db.enabled():
        statements = [(
            "INSERT INTO SCREENING (screening_id, movie_id, screen_id, "
            "screening_date, screening_time, screening_type) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (screening.screening_id, screening.movie.movie_id,
             screening.screen.screen_id, screening.date, screening.time,
             screening.screening_type),
        )]
        # One SCREENING_SEAT row per physical seat, all starting free.
        for screening_seat in screening.seat_map.values():
            statements.append((
                "INSERT INTO SCREENING_SEAT (screening_seat_id, "
                "screening_id, seat_id, is_booked) VALUES (?, ?, ?, 0)",
                (screening_seat.screening_seat_id, screening.screening_id,
                 screening_seat.seat.seat_id),
            ))
        db.execute_transaction(statements)


def save(screening):
    """UPDATE after the date, time, or type is edited."""
    if db.enabled():
        db.execute(
            "UPDATE SCREENING SET screening_date = ?, screening_time = ?, "
            "screening_type = ? WHERE screening_id = ?",
            (screening.date, screening.time, screening.screening_type,
             screening.screening_id))


def next_id():
    return f"SC-{len(SCREENINGS) + 1:02d}"


def find_screen_by_number(screen_number):
    for screen in SCREENS:
        if screen.screen_number == screen_number:
            return screen
    return None
