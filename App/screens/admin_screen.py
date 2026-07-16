"""
==========================================
[Member 1] Manager Administration screen
==========================================
Managers maintain the movie catalogue (add, edit, deactivate, restore)
and the screening schedule (add new screenings, update date/time/type).
The sidebar already blocks Cashiers from opening this screen, and the
business logic checks permissions again -- defence in two layers.
"""

import customtkinter as ctk
from tkinter import messagebox

from business_logic import movie_service
import config
from widgets.base_screen import BaseScreen
from widgets.table import DataTable, Badge, Button
from business_logic import screening_service

TYPE_BADGES = {
    "Standard": ("#f1f5f9", "#475569"),
    "IMAX": ("#ede9fe", "#5b21b6"),
    "Kids": ("#dcfce7", "#15803d"),
}


class AdminScreen(BaseScreen):

    title = "Manager Administration"

    def build(self):
        tabs = ctk.CTkTabview(self.content, fg_color=config.CARD_BG,
                              segmented_button_selected_color=config.PRIMARY,
                              segmented_button_selected_hover_color=config.PRIMARY_HOVER)
        tabs.pack(fill="both", expand=True)
        movies_tab = tabs.add("Movies")
        screenings_tab = tabs.add("Screenings")

        # ---- Movies tab ----
        bar = ctk.CTkFrame(movies_tab, fg_color="transparent")
        bar.pack(fill="x", pady=(4, 10))
        ctk.CTkButton(bar, text="+ Add Movie", height=34,
                      fg_color=config.PRIMARY, hover_color=config.PRIMARY_HOVER,
                      font=config.FONT_NORMAL,
                      command=lambda: self.open_dialog(None)).pack(side="right")

        self.movies_table = DataTable(
            movies_tab,
            columns=["TITLE", "GENRE", "DURATION", "RATING", "STATUS", "", ""],
            weights=[4, 2, 2, 2, 2, 2, 2])
        self.movies_table.pack(fill="both", expand=True)

        # ---- Screenings tab (add / edit) ----
        sbar = ctk.CTkFrame(screenings_tab, fg_color="transparent")
        sbar.pack(fill="x", pady=(4, 10))
        ctk.CTkButton(sbar, text="+ Add Screening", height=34,
                      fg_color=config.PRIMARY, hover_color=config.PRIMARY_HOVER,
                      font=config.FONT_NORMAL,
                      command=lambda: self.open_screening_dialog(None)).pack(side="right")

        self.screenings_table = DataTable(
            screenings_tab,
            columns=["MOVIE", "DATE", "TIME", "SCREEN", "TYPE", "OCCUPANCY", ""],
            weights=[4, 2, 2, 1, 2, 2, 2])
        self.screenings_table.pack(fill="both", expand=True, pady=(4, 0))

    def refresh(self):
        rows = []
        for m in movie_service.list_movies():
            if m.is_active:
                actions = [
                    Button("Edit", lambda mv=m: self.open_dialog(mv),
                           color="#64748b", hover="#475569"),
                    Button("Delete", lambda mv=m: self.deactivate(mv),
                           color=config.DANGER, hover="#b91c1c"),
                ]
                status = Badge("Active", "#dcfce7", "#15803d")
            else:
                actions = [
                    Button("Restore", lambda mv=m: self.restore(mv),
                           color=config.SUCCESS, hover="#15803d"),
                    "",
                ]
                status = Badge("Inactive", "#f1f5f9", "#64748b")
            rows.append([m.title, m.genre, m.duration_text, m.rating, status] + actions)
        self.movies_table.set_rows(rows)

        self.screenings_table.set_rows([
            [s.movie.title, s.date, s.time, str(s.screen.screen_number),
             Badge(s.screening_type, *TYPE_BADGES.get(s.screening_type, ("#f1f5f9", "#475569"))),
             f"{s.occupancy_percent}%",
             Button("Edit", lambda sc=s: self.open_screening_dialog(sc),
                    color="#64748b", hover="#475569")]
            for s in screening_service.list_screenings()
        ])

    def deactivate(self, movie):
        if not messagebox.askyesno("Deactivate Movie",
                                   f"Mark '{movie.title}' as no longer showing?"):
            return
        try:
            movie_service.deactivate_movie(self.controller.current_user, movie)
        except PermissionError as error:
            messagebox.showwarning("Access Denied", str(error))
            return
        self.refresh()

    def restore(self, movie):
        try:
            movie_service.restore_movie(self.controller.current_user, movie)
        except PermissionError as error:
            messagebox.showwarning("Access Denied", str(error))
            return
        self.refresh()

    def open_dialog(self, movie):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Movie" if movie is None else "Edit Movie")
        dialog.geometry("360x360")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        entries = {}
        for field, value in [("Title", movie.title if movie else ""),
                             ("Duration (minutes)", str(movie.duration_min) if movie else ""),
                             ("Rating (e.g. PG-13)", movie.rating if movie else "")]:
            ctk.CTkLabel(dialog, text=field, font=config.FONT_SMALL).pack(
                anchor="w", padx=24, pady=(10, 2))
            entry = ctk.CTkEntry(dialog, height=34, font=config.FONT_NORMAL)
            entry.insert(0, value)
            entry.pack(fill="x", padx=24)
            entries[field] = entry

        ctk.CTkLabel(dialog, text="Genre", font=config.FONT_SMALL).pack(
            anchor="w", padx=24, pady=(10, 2))
        genres = [g for g in movie_service.get_genres() if g != "All"]
        genre_menu = ctk.CTkOptionMenu(dialog, values=genres, height=34,
                                       fg_color=config.PAGE_BG, text_color=config.TEXT,
                                       button_color=config.PRIMARY)
        genre_menu.set(movie.genre if movie else genres[0])
        genre_menu.pack(fill="x", padx=24)

        def save():
            try:
                args = (entries["Title"].get(), genre_menu.get(),
                        entries["Duration (minutes)"].get(),
                        entries["Rating (e.g. PG-13)"].get())
                if movie is None:
                    movie_service.add_movie(self.controller.current_user, *args)
                else:
                    movie_service.edit_movie(self.controller.current_user, movie, *args)
            except (ValueError, PermissionError) as error:
                messagebox.showwarning("Check Input", str(error), parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(dialog, text="Save", height=38, fg_color=config.PRIMARY,
                      hover_color=config.PRIMARY_HOVER, font=config.FONT_NORMAL,
                      command=save).pack(fill="x", padx=24, pady=16)

    def open_screening_dialog(self, screening):
        """Add a new screening, or edit an existing one's date/time/type.
        The movie and screen are fixed after creation (their seat map --
        and any bookings on it -- belongs to that screen)."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Screening" if screening is None else "Edit Screening")
        dialog.geometry("360x420")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        def dropdown(label, values, initial, enabled=True):
            ctk.CTkLabel(dialog, text=label, font=config.FONT_SMALL).pack(
                anchor="w", padx=24, pady=(10, 2))
            menu = ctk.CTkOptionMenu(dialog, values=values, height=34,
                                     fg_color=config.PAGE_BG, text_color=config.TEXT,
                                     button_color=config.PRIMARY)
            menu.set(initial)
            if not enabled:
                menu.configure(state="disabled")
            menu.pack(fill="x", padx=24)
            return menu

        movies = screening_service.list_active_movie_titles() or ["(no active movies)"]
        movie_menu = dropdown(
            "Movie", movies,
            screening.movie.title if screening else movies[0],
            enabled=screening is None)

        screen_numbers = [str(n) for n in screening_service.get_screen_numbers()]
        screen_menu = dropdown(
            "Screen", screen_numbers,
            str(screening.screen.screen_number) if screening else screen_numbers[0],
            enabled=screening is None)

        entries = {}
        for field, value in [("Date (YYYY-MM-DD)", screening.date if screening else ""),
                             ("Time (e.g. 7:00 PM)", screening.time if screening else "")]:
            ctk.CTkLabel(dialog, text=field, font=config.FONT_SMALL).pack(
                anchor="w", padx=24, pady=(10, 2))
            entry = ctk.CTkEntry(dialog, height=34, font=config.FONT_NORMAL)
            entry.insert(0, value)
            entry.pack(fill="x", padx=24)
            entries[field] = entry

        type_menu = dropdown(
            "Screening type", screening_service.get_screening_types(),
            screening.screening_type if screening
            else screening_service.get_screening_types()[0])

        def save():
            try:
                date_text = entries["Date (YYYY-MM-DD)"].get()
                time_text = entries["Time (e.g. 7:00 PM)"].get()
                if screening is None:
                    screening_service.add_screening(
                        self.controller.current_user, movie_menu.get(),
                        int(screen_menu.get()), date_text, time_text,
                        type_menu.get())
                else:
                    screening_service.edit_screening(
                        self.controller.current_user, screening,
                        date_text, time_text, type_menu.get())
            except (ValueError, PermissionError) as error:
                messagebox.showwarning("Check Input", str(error), parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(dialog, text="Save", height=38, fg_color=config.PRIMARY,
                      hover_color=config.PRIMARY_HOVER, font=config.FONT_NORMAL,
                      command=save).pack(fill="x", padx=24, pady=16)

    def on_show(self):
        super().on_show()
        self.refresh()
