"""
==========================================
Domain Model - Staff  [Member 1]
==========================================
OOP concepts demonstrated here:
- ABSTRACTION:   Staff is an abstract base class (cannot be instantiated).
- INHERITANCE:   Cashier and Manager both inherit from Staff.
- POLYMORPHISM:  get_permissions() is abstract and each subclass returns
                 its own permission set; callers never check the role name,
                 they just ask "what can this user do?".
- ENCAPSULATION: the password is checked inside login(); no other code
                 reads the _password attribute directly.
"""

from abc import ABC, abstractmethod


class Staff(ABC):
    """Abstract base class for anyone who logs into the system."""

    def __init__(self, staff_id, username, password, name):
        self.staff_id = staff_id
        self.username = username
        self._password = password   # encapsulated: only login() reads this
        self.name = name
        self.is_logged_in = False

    def login(self, password):
        """Marks the session active if the password matches."""
        self.is_logged_in = password == self._password
        return self.is_logged_in

    def logout(self):
        self.is_logged_in = False

    @property
    @abstractmethod
    def role(self):
        raise NotImplementedError

    @abstractmethod
    def get_permissions(self):
        """Return the set of permission strings this staff member has.
        Overridden by each subclass (polymorphism)."""
        raise NotImplementedError

    def can(self, permission):
        return permission in self.get_permissions()


class Cashier(Staff):
    """Handles day-to-day customer bookings."""

    role = "Cashier"

    def get_permissions(self):
        return {"booking"}

    def book_ticket(self, booking):
        """Confirms a booking created at the counter."""
        return booking.confirm_booking()


class Manager(Staff):
    """Everything a Cashier can do, plus catalogue management and reports."""

    role = "Manager"

    def get_permissions(self):
        return {"booking", "catalogue", "reports"}

    def book_ticket(self, booking):
        return booking.confirm_booking()

    def add_movie(self, catalogue, movie):
        catalogue.append(movie)
        return movie

    def update_movie(self, movie, **fields):
        movie.update_movie(**fields)
        return movie

    def deactivate_movie(self, movie):
        movie.is_active = False

    def view_reports(self, reports):
        """reports: list of Report objects -- polymorphic generate() calls."""
        return [report.generate() for report in reports]
