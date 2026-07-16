"""
Business Logic - Reports & dashboard stats  [Member 5]
Every number here is computed LIVE from the current objects using the
Report class hierarchy -- nothing is hard-coded (assignment rule).
"""
from data_access import booking_repository, customer_repository
from data_access import screening_repository
from business_logic.auth_service import require_permission
from models.report import (RevenueReport, TopMoviesReport,
                           SeatOccupancyReport, MembershipDistributionReport)


def dashboard_stats():
    bookings = booking_repository.get_all()
    tickets = sum(len(b.screening_seats) for b in bookings)
    return {
        "revenue": round(sum(b.final_amount for b in bookings), 2),
        "bookings": len(bookings),
        "tickets": tickets,
        "customers": len(customer_repository.get_all()),
    }


def generate_all_reports(current_user):
    """Manager-only. Returns the four generated report dicts, produced
    polymorphically -- the caller never knows which subclass made which."""
    require_permission(current_user, "reports")
    reports = [
        RevenueReport(booking_repository.get_all()),
        TopMoviesReport(booking_repository.get_all()),
        SeatOccupancyReport(screening_repository.get_all()),
        MembershipDistributionReport(customer_repository.get_all()),
    ]
    return [r.generate() for r in reports]
