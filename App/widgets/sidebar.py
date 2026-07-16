"""
==========================================
Shared widget - Sidebar  [shared - ask team before editing]
==========================================
The left navigation menu, shown on every screen after login. It also
displays the logged-in staff member's name and role (the assignment
requires the name to be visible on ALL screens).

Menu items can require a permission: clicking Administration or Reports
as a Cashier shows a clear "access denied" message instead of opening
the screen -- the role check uses the polymorphic get_permissions().
"""

import customtkinter as ctk
from tkinter import messagebox

import config

# (label, screen class name, required permission or None)
MENU_ITEMS = [
    ("Dashboard", "DashboardScreen", None),
    ("Customers", "CustomersScreen", None),
    ("Movie Browser", "MoviesScreen", None),
    ("Screenings", "ScreeningsScreen", None),
    ("New Booking", "BookingScreen", "booking"),
    ("Administration", "AdminScreen", "catalogue"),
    ("Reports", "ReportsScreen", "reports"),
]


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, controller, active_screen):
        super().__init__(parent, width=220, corner_radius=0,
                         fg_color=config.SIDEBAR_BG)
        self.controller = controller
        self.pack_propagate(False)

        # ---- Logo ----
        ctk.CTkLabel(self, text="StarScreen", font=config.FONT_HEADING,
                     text_color="white").pack(anchor="w", padx=20, pady=(24, 0))
        ctk.CTkLabel(self, text="CINEMAS", font=config.FONT_SMALL,
                     text_color="#93c5fd").pack(anchor="w", padx=20, pady=(0, 20))

        # ---- Menu buttons ----
        for label, screen_name, permission in MENU_ITEMS:
            is_active = screen_name == active_screen
            ctk.CTkButton(
                self, text=label, anchor="w", height=38, corner_radius=8,
                font=config.FONT_NORMAL,
                fg_color=config.PRIMARY if is_active else "transparent",
                hover_color=config.PRIMARY if is_active else config.SIDEBAR_HOVER,
                command=lambda s=screen_name, p=permission: self._navigate(s, p),
            ).pack(fill="x", padx=12, pady=3)

        # ---- Bottom: logged-in user + logout ----
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=20, pady=18)
        self.name_label = ctk.CTkLabel(bottom, text="", font=config.FONT_NORMAL,
                                       text_color="white", anchor="w")
        self.name_label.pack(anchor="w")
        self.role_label = ctk.CTkLabel(bottom, text="", font=config.FONT_SMALL,
                                       text_color="#93c5fd", anchor="w")
        self.role_label.pack(anchor="w")
        ctk.CTkButton(bottom, text="Logout", height=30, corner_radius=8,
                      fg_color=config.SIDEBAR_HOVER, hover_color="#475569",
                      font=config.FONT_SMALL,
                      command=controller.logout).pack(fill="x", pady=(10, 0))

        self.refresh_user()

    def _navigate(self, screen_name, permission):
        """Block restricted screens with a clear message (never crash)."""
        user = self.controller.current_user
        if permission and (user is None or not user.can(permission)):
            messagebox.showwarning(
                "Access Denied",
                "This function is only available to Managers.")
            return
        self.controller.show_frame(screen_name)

    def refresh_user(self):
        user = self.controller.current_user
        self.name_label.configure(text=user.name if user else "Guest")
        self.role_label.configure(text=user.role if user else "")
