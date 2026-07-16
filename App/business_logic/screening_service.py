"""
Business Logic - Screenings  [Member 3]
Managers can also add new screenings and update existing ones
(assignment rule: "Managers can ... update screening details").
Validation raises ValueError with a clear message -- the UI shows it,
the app never crashes.
"""
import datetime

from data_access import movie_repository
from data_access import screening_repository
from business_logic.auth_service import require_permission
from models.screening import Screening


def list_screenings(movie_filter="All", type_filter="All"):
    return [
        s for s in screening_repository.get_all()
        if (movie_filter in ("All", "") or s.movie.title == movie_filter)
        and (type_filter in ("All", "") or s.screening_type == type_filter)
    ]


def list_active_screenings():
    """Only screenings of movies still showing can be booked."""
    return [s for s in screening_repository.get_all() if s.movie.is_active]


def get_all_movie_titles():
    return sorted({s.movie.title for s in screening_repository.get_all()})


def get_screening_types():
    return screening_repository.get_screening_types()


def find_by_label(label):
    for s in screening_repository.get_all():
        if s.label == label:
            return s
    return None


def get_screen_numbers():
    return [s.screen_number for s in screening_repository.get_screens()]


def list_active_movie_titles():
    """Only currently-showing movies can be scheduled."""
    return [m.title for m in movie_repository.get_all() if m.is_active]


def _validate_date(date_text):
    """Accepts YYYY-MM-DD; returns the normalised string."""
    try:
        return datetime.date.fromisoformat((date_text or "").strip()).isoformat()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format, e.g. 2026-08-01.")


def _validate_time(time_text):
    """Accepts times like '7:00 PM'; returns the normalised string."""
    time_text = (time_text or "").strip().upper()
    try:
        parsed = datetime.datetime.strptime(time_text, "%I:%M %p")
    except ValueError:
        raise ValueError("Time must look like 7:00 PM or 10:30 AM.")
    return parsed.strftime("%I:%M %p").lstrip("0")


def _check_no_clash(screen, date, time, ignore=None):
    """One screen cannot host two screenings at the same date and time."""
    for s in screening_repository.get_all():
        if s is ignore:
            continue
        if s.screen is screen and s.date == date and s.time == time:
            raise ValueError(
                f"Screen {screen.screen_number} already has "
                f"'{s.movie.title}' at {time} on {date}.")


def add_screening(current_user, movie_title, screen_number, date_text,
                  time_text, screening_type):
    """Manager-only: schedule a new screening with an empty seat map."""
    require_permission(current_user, "catalogue")

    movie = next((m for m in movie_repository.get_all()
                  if m.title == movie_title and m.is_active), None)
    if movie is None:
        raise ValueError("Please choose a currently showing movie.")

    screen = screening_repository.find_screen_by_number(screen_number)
    if screen is None:
        raise ValueError("Please choose a valid screen.")

    if screening_type not in get_screening_types():
        raise ValueError("Please choose a screening type.")

    date = _validate_date(date_text)
    time = _validate_time(time_text)
    _check_no_clash(screen, date, time)

    screening = Screening(screening_repository.next_id(), movie, screen,
                          date, time, screening_type)
    screening_repository.add(screening)
    return screening


def edit_screening(current_user, screening, date_text, time_text,
                   screening_type):
    """Manager-only: update a screening's date, time, or type. The movie
    and screen stay fixed -- the seat map (and any bookings on it)
    belongs to this screen, so moving it would orphan booked seats."""
    require_permission(current_user, "catalogue")

    if screening_type not in get_screening_types():
        raise ValueError("Please choose a screening type.")

    date = _validate_date(date_text)
    time = _validate_time(time_text)
    _check_no_clash(screening.screen, date, time, ignore=screening)

    booked = screening.seats_total - screening.get_available_seats()
    if screening_type != screening.screening_type and booked > 0:
        raise ValueError(
            f"Cannot change the screening type: {booked} seat(s) are "
            "already booked at the current prices.")

    screening.date = date
    screening.time = time
    screening.screening_type = screening_type
    screening_repository.save(screening)   # write-through to SQL Server
    return screening
