"""
==========================================
[Member 1] Login screen
==========================================
Staff sign in with a username and password. On success the actual
Cashier/Manager object is stored on controller.current_user, and every
later role check asks that object what it can do (polymorphism).
"""

import customtkinter as ctk
from tkinter import messagebox

import config
from business_logic import auth_service


class LoginScreen(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=config.PAGE_BG, corner_radius=0)
        self.controller = controller

        card = ctk.CTkFrame(self, fg_color=config.CARD_BG, corner_radius=14, width=400)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # ---- Blue header ----
        header = ctk.CTkFrame(card, fg_color=config.PRIMARY,
                              height=120)
        header.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(header, text="StarScreen", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(pady=(22, 0))
        ctk.CTkLabel(header, text="CINEMAS  \u00b7  MANAGEMENT SYSTEM",
                     font=config.FONT_SMALL, text_color="#bfdbfe").pack(pady=(0, 20))

        # ---- Form ----
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=32, pady=24)

        ctk.CTkLabel(body, text="Sign In", font=config.FONT_HEADING,
                     text_color=config.TEXT).pack(anchor="center", pady=(0, 12))

        self.username_entry = ctk.CTkEntry(body, placeholder_text="Username",
                                           height=38, font=config.FONT_NORMAL)
        self.username_entry.pack(fill="x", pady=(0, 10))

        self.password_entry = ctk.CTkEntry(body, placeholder_text="Password",
                                           show="*", height=38, font=config.FONT_NORMAL)
        self.password_entry.pack(fill="x", pady=(0, 16))
        self.password_entry.bind("<Return>", lambda e: self.handle_login())

        ctk.CTkButton(body, text="Login", height=40, font=config.FONT_NORMAL,
                      fg_color=config.PRIMARY, hover_color=config.PRIMARY_HOVER,
                      command=self.handle_login).pack(fill="x")

        ctk.CTkLabel(body, text="Demo accounts", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT).pack(pady=(18, 4))
        ctk.CTkLabel(body, text="cashier / cashier123      manager / manager123",
                     font=config.FONT_SMALL, text_color=config.TEXT_LIGHT).pack(pady=(0, 4))

    def handle_login(self):
        user = auth_service.login(self.username_entry.get(), self.password_entry.get())
        if user is None:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            return
        self.controller.current_user = user
        self.controller.show_frame("DashboardScreen")

    def on_show(self):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.username_entry.focus()
