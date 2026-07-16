"""
==========================================
[Member 1] Dashboard screen
==========================================
The first screen after login: four live stat cards (computed from the
current data, not hard-coded), recent bookings, and what's now showing.
"""

import customtkinter as ctk

from business_logic import booking_service, movie_service
import config
from widgets.base_screen import BaseScreen
from widgets.table import DataTable, Badge
from business_logic import report_service


class DashboardScreen(BaseScreen):

    title = "Dashboard"

    def build(self):
        # ---- Stat cards ----
        self.cards_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.cards_row.pack(fill="x", pady=(0, 16))
        self.stat_labels = {}
        for key, caption in [("revenue", "TOTAL REVENUE"), ("bookings", "BOOKINGS"),
                             ("tickets", "TICKETS SOLD"), ("customers", "MEMBERS")]:
            card = self.card(self.cards_row)
            card.pack(side="left", expand=True, fill="x", padx=6)
            value = ctk.CTkLabel(card, text="-", font=("Segoe UI", 24, "bold"),
                                 text_color=config.TEXT, anchor="w")
            value.pack(anchor="w", padx=16, pady=(14, 0))
            ctk.CTkLabel(card, text=caption, font=config.FONT_SMALL,
                         text_color=config.TEXT_LIGHT, anchor="w").pack(
                anchor="w", padx=16, pady=(0, 14))
            self.stat_labels[key] = value

        # ---- Bottom: recent bookings (left) + now showing (right) ----
        bottom = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom.pack(fill="both", expand=True)

        left = ctk.CTkFrame(bottom, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        ctk.CTkLabel(left, text="RECENT BOOKINGS", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, anchor="w").pack(fill="x", pady=(0, 6))
        self.bookings_table = DataTable(
            left, columns=["BOOKING", "CUSTOMER", "MOVIE", "SEATS", "TOTAL"],
            weights=[2, 3, 3, 2, 2])
        self.bookings_table.pack(fill="both", expand=True)

        right = self.card(bottom, width=280)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)
        ctk.CTkLabel(right, text="NOW SHOWING", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, anchor="w").pack(
            fill="x", padx=16, pady=(14, 6))
        self.now_showing_box = ctk.CTkFrame(right, fg_color="transparent")
        self.now_showing_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def refresh(self):
        stats = report_service.dashboard_stats()
        self.stat_labels["revenue"].configure(text=f"${stats['revenue']:,.2f}")
        self.stat_labels["bookings"].configure(text=str(stats["bookings"]))
        self.stat_labels["tickets"].configure(text=str(stats["tickets"]))
        self.stat_labels["customers"].configure(text=str(stats["customers"]))

        self.bookings_table.set_rows([
            [b.booking_id, b.customer.name, b.screening.movie.title,
             ", ".join(ss.seat.seat_number for ss in b.screening_seats),
             f"${b.final_amount:.2f}"]
            for b in booking_service.list_recent_bookings(limit=8)
        ])

        for widget in self.now_showing_box.winfo_children():
            widget.destroy()
        for m in movie_service.list_movies(active_only=True):
            ctk.CTkLabel(self.now_showing_box, text=m.title,
                         font=config.FONT_NORMAL, text_color=config.TEXT,
                         anchor="w").pack(fill="x", pady=(6, 0))
            ctk.CTkLabel(self.now_showing_box,
                         text=f"{m.genre} \u00b7 {m.duration_text} \u00b7 {m.rating}",
                         font=config.FONT_SMALL, text_color=config.TEXT_LIGHT,
                         anchor="w").pack(fill="x")

    def on_show(self):
        super().on_show()
        self.refresh()
