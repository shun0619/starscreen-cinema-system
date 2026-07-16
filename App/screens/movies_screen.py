"""
==========================================
[Member 3] Movie Browser screen
==========================================
Browse currently showing movies and filter by genre (assignment
requirement). The genre filter is a segmented button -- one widget
instead of seven hand-styled buttons.
"""

import customtkinter as ctk

import config as config
from widgets.base_screen import BaseScreen
from widgets.table import DataTable, Badge
from business_logic import movie_service


class MoviesScreen(BaseScreen):

    title = "Movie Browser"

    def build(self):
        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(bar, placeholder_text="Search movies...",
                                         height=36, font=config.FONT_NORMAL)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self.genre_filter = ctk.CTkSegmentedButton(
            bar, values=movie_service.get_genres(),
            command=lambda _: self.refresh(), height=36,
            font=config.FONT_SMALL, selected_color=config.PRIMARY,
            selected_hover_color=config.PRIMARY_HOVER)
        self.genre_filter.set("All")
        self.genre_filter.pack(side="left")

        self.table = DataTable(
            self.content,
            columns=["TITLE", "GENRE", "DURATION", "RATING", "STATUS"],
            weights=[4, 2, 2, 2, 2])
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        rows = []
        for m in movie_service.list_movies(self.genre_filter.get(),
                                           self.search_entry.get()):
            status_badge = (Badge("Active", "#dcfce7", "#15803d") if m.is_active
                            else Badge("Inactive", "#f1f5f9", "#64748b"))
            rows.append([m.title, m.genre, m.duration_text, m.rating, status_badge])
        self.table.set_rows(rows)

    def on_show(self):
        super().on_show()
        self.refresh()
