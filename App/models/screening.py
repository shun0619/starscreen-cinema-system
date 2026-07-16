"""
==========================================
Domain Model - Screen & Screening  [Member 3]
==========================================
StarScreen has three physical screens. Each Screening (a showtime of a
movie on one screen) owns its OWN seat map of ScreeningSeat objects, so
booking seat A5 at 2pm doesn't block A5 at 7pm.
"""

from models.seat import ScreeningSeat


class Screen:

    def __init__(self, screen_id, screen_number, seats):
        self.screen_id = screen_id
        self.screen_number = screen_number  # 1, 2, 3
        self.seats = seats                  # list of Seat (the physical layout)

    @property
    def capacity(self):
        return len(self.seats)


class Screening:

    def __init__(self, screening_id, movie, screen, date, time, screening_type,
                 pre_booked=None):
        self.screening_id = screening_id
        self.movie = movie                  # Movie instance
        self.screen = screen                # Screen instance
        self.date = date                    # "YYYY-MM-DD"
        self.time = time                    # "7:00 PM"
        self.screening_type = screening_type  # Standard / IMAX / Kids

        # Build this screening's own seat availability map:
        # {(row, number): ScreeningSeat}
        pre_booked = pre_booked or set()
        self.seat_map = {}
        for seat in screen.seats:
            key = (seat.row, seat.number)
            self.seat_map[key] = ScreeningSeat(
                screening_seat_id=f"{screening_id}-{seat.seat_number}",
                seat=seat,
                is_booked=key in pre_booked,
            )

    def get_available_seats(self):
        return sum(1 for ss in self.seat_map.values() if not ss.is_booked)

    @property
    def seats_total(self):
        return len(self.seat_map)

    @property
    def occupancy_percent(self):
        if not self.seat_map:
            return 0
        booked = self.seats_total - self.get_available_seats()
        return round(100 * booked / self.seats_total)

    @property
    def label(self):
        """Readable one-liner used in dropdowns."""
        return f"{self.movie.title}  |  {self.date} {self.time}  |  Screen {self.screen.screen_number} ({self.screening_type})"
