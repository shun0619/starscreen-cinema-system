"""
==========================================
Domain Model - Reports  [Member 5]
==========================================
Report is abstract; each subclass computes its own summary from live
objects (never hard-coded numbers). The Reports screen calls generate()
without caring which subclass it holds -- polymorphism in action.
"""

from abc import ABC, abstractmethod


class Report(ABC):

    def __init__(self, report_name):
        self.report_name = report_name

    @abstractmethod
    def generate(self):
        raise NotImplementedError


class RevenueReport(Report):
    """Today's revenue broken down by membership tier (assignment option 1)."""

    def __init__(self, bookings):
        super().__init__("Daily Revenue by Tier")
        self.bookings = bookings

    def generate(self):
        by_tier = {}
        for b in self.bookings:
            tier = b.customer.get_membership_tier()
            by_tier[tier] = by_tier.get(tier, 0) + b.final_amount
        return {"report_name": self.report_name, "revenue_by_tier": by_tier,
                "total": round(sum(by_tier.values()), 2)}


class TopMoviesReport(Report):
    """Movies ranked by tickets (seats) sold (assignment option 2)."""

    def __init__(self, bookings):
        super().__init__("Top Movies by Tickets Sold")
        self.bookings = bookings

    def generate(self):
        counts = {}
        for b in self.bookings:
            title = b.screening.movie.title
            counts[title] = counts.get(title, 0) + len(b.screening_seats)
        ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        return {"report_name": self.report_name, "top_movies": ranked}


class SeatOccupancyReport(Report):
    """Percentage of seats filled per screen (assignment option 3)."""

    def __init__(self, screenings):
        super().__init__("Seat Occupancy by Screen")
        self.screenings = screenings

    def generate(self):
        per_screen = {}
        for s in self.screenings:
            per_screen.setdefault(s.screen.screen_number, []).append(s.occupancy_percent)
        averaged = {
            f"Screen {num}": round(sum(vals) / len(vals))
            for num, vals in sorted(per_screen.items())
        }
        return {"report_name": self.report_name, "occupancy": averaged}


class MembershipDistributionReport(Report):
    """Count and percentage of customers per tier (assignment option 4)."""

    def __init__(self, customers):
        super().__init__("Membership Distribution")
        self.customers = customers

    def generate(self):
        counts = {}
        for c in self.customers:
            tier = c.get_membership_tier()
            counts[tier] = counts.get(tier, 0) + 1
        total = sum(counts.values()) or 1
        percentages = {tier: round(100 * n / total) for tier, n in counts.items()}
        return {"report_name": self.report_name, "counts": counts,
                "percentages": percentages, "total": total}
