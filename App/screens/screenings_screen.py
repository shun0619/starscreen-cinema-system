"""
==========================================
[Member 3] Screening Management screen
==========================================
Shows every screening with LIVE seat availability (computed from each
screening's own seat map, so it updates the moment a booking happens).
The Book button jumps to New Booking with the screening pre-selected.
"""

import customtkinter as ctk

import config
from widgets.base_screen import BaseScreen
from widgets.table import DataTable, Badge, Button
from business_logic import screening_service

TYPE_BADGES = {
    "Standard": ("#f1f5f9", "#475569"),
    "IMAX": ("#ede9fe", "#5b21b6"),
    "Kids": ("#dcfce7", "#15803d"),
}


class ScreeningsScreen(BaseScreen):

    title = "Screening"

    def build(self):
        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 10))

        self.movie_menu = ctk.CTkOptionMenu(
            bar, values=["All"] + screening_service.get_all_movie_titles(),
            command=lambda _: self.refresh(), width=220, height=36,
            fg_color=config.CARD_BG, text_color=config.TEXT,
            button_color=config.PRIMARY, font=config.FONT_NORMAL)
        self.movie_menu.set("All")
        self.movie_menu.pack(side="left", padx=(0, 10))

        self.type_menu = ctk.CTkOptionMenu(
            bar, values=["All"] + screening_service.get_screening_types(),
            command=lambda _: self.refresh(), width=140, height=36,
            fg_color=config.CARD_BG, text_color=config.TEXT,
            button_color=config.PRIMARY, font=config.FONT_NORMAL)
        self.type_menu.set("All")
        self.type_menu.pack(side="left")

        self.count_label = ctk.CTkLabel(bar, text="", font=config.FONT_SMALL,
                                        text_color=config.TEXT_LIGHT)
        self.count_label.pack(side="right")

        self.table = DataTable(
            self.content,
            columns=["MOVIE", "DATE", "TIME", "SCREEN", "TYPE", "SEATS FREE", ""],
            weights=[4, 2, 2, 1, 2, 2, 2])
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        screenings = screening_service.list_screenings(self.movie_menu.get(),
                                                       self.type_menu.get())
        rows = []
        for s in screenings:
            bg, fg = TYPE_BADGES.get(s.screening_type, ("#f1f5f9", "#475569"))
            rows.append([
                s.movie.title, s.date, s.time, str(s.screen.screen_number),
                Badge(s.screening_type, bg, fg),
                f"{s.get_available_seats()}/{s.seats_total}",
                Button("Book", lambda sc=s: self.go_to_booking(sc)),
            ])
        self.table.set_rows(rows)
        self.count_label.configure(text=f"{len(screenings)} screenings")

    def go_to_booking(self, screening):
        self.controller.prefill_screening = screening
        self.controller.show_frame("BookingScreen")

    def on_show(self):
        super().on_show()
        self.refresh()
