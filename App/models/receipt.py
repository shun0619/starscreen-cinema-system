"""
==========================================
Domain Model - Receipt  [Member 4]
==========================================
Generated automatically after every completed booking. Shows everything
the assignment requires: cinema name, movie/screening details, seats,
customer + tier, itemised price breakdown, payment method, points
earned, new balance, and the staff member's name.
"""

import config


class Receipt:

    def __init__(self, receipt_id, booking, payment):
        self.receipt_id = receipt_id
        self.booking = booking
        self.payment = payment

    def generate_receipt(self):
        b, p = self.booking, self.payment
        seats = ", ".join(ss.seat.seat_number for ss in b.screening_seats)
        lines = [
            f"{config.APP_NAME}",
            f"Receipt {self.receipt_id}",
            "=" * 40,
            f"Movie:      {b.screening.movie.title}",
            f"Screening:  {b.screening.date} {b.screening.time}",
            f"Screen:     {b.screening.screen.screen_number} ({b.screening.screening_type})",
            f"Seats:      {seats}",
            "-" * 40,
            f"Customer:   {b.customer.name}",
            f"Membership: {b.customer.get_membership_tier()}",
            "-" * 40,
            f"Subtotal:          ${b.subtotal:>8.2f}",
            f"Discount:         -${b.discount_amount:>8.2f}",
            f"GST ({config.GST_PERCENT}%):         +${b.gst_amount:>8.2f}",
            f"TOTAL:             ${b.final_amount:>8.2f}",
            "-" * 40,
            f"Paid by:    {p.payment_method}",
        ]
        if p.payment_method == "Cash":
            lines.append(f"Tendered:          ${p.cash_tendered:>8.2f}")
            lines.append(f"Change due:        ${p.change_due:>8.2f}")
        lines += [
            "-" * 40,
            f"Points earned:  {b.points_earned}",
            f"Points balance: {b.customer.points}",
            f"Served by:      {b.staff.name}",
            "=" * 40,
            "Thank you and enjoy the movie!",
        ]
        return "\n".join(lines)
