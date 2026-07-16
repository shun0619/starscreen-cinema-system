"""
==========================================
[Member 2] Customer Management screen
==========================================
Register new customers (they start as Regular Members), update details,
filter by tier, and view a customer's booking history -- all assignment
requirements. Tier badges are colored per tier.
"""

import customtkinter as ctk
from tkinter import messagebox

from business_logic import booking_service
import config
from widgets.base_screen import BaseScreen
from widgets.table import DataTable, Badge, Button
from business_logic import customer_service


class CustomersScreen(BaseScreen):

    title = "Customer Management"

    def build(self):
        # ---- Toolbar: search + tier filter + add button ----
        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(bar, placeholder_text="Search by name or email...",
                                         height=36, font=config.FONT_NORMAL)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self.tier_menu = ctk.CTkOptionMenu(
            bar, values=["All"] + customer_service.get_tier_names(),
            command=lambda _: self.refresh(), width=130, height=36,
            fg_color=config.CARD_BG, text_color=config.TEXT,
            button_color=config.PRIMARY, font=config.FONT_NORMAL)
        self.tier_menu.set("All")
        self.tier_menu.pack(side="left", padx=10)

        ctk.CTkButton(bar, text="+ Register Customer", height=36,
                      fg_color=config.PRIMARY, hover_color=config.PRIMARY_HOVER,
                      font=config.FONT_NORMAL,
                      command=lambda: self.open_dialog(None)).pack(side="left")

        # ---- Table ----
        self.table = DataTable(
            self.content,
            columns=["ID", "NAME", "EMAIL", "PHONE", "TIER", "POINTS", "", ""],
            weights=[2, 3, 4, 3, 2, 2, 2, 2])
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        rows = []
        for c in customer_service.list_customers(self.search_entry.get(),
                                                 self.tier_menu.get()):
            bg, fg = customer_service.get_tier_badge(c.get_membership_tier())
            rows.append([
                c.customer_id, c.name, c.email, c.phone,
                Badge(c.get_membership_tier(), bg, fg),
                f"{c.points:,}",
                Button("Edit", lambda cu=c: self.open_dialog(cu),
                       color="#64748b", hover="#475569"),
                Button("History", lambda cu=c: self.show_history(cu)),
            ])
        self.table.set_rows(rows)

    def open_dialog(self, customer):
        """One dialog handles both Register (customer=None) and Edit."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Register Customer" if customer is None else "Edit Customer")
        dialog.geometry("360x340")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        entries = {}
        for field, value in [("Name", customer.name if customer else ""),
                             ("Phone", customer.phone if customer else ""),
                             ("Email", customer.email if customer else "")]:
            ctk.CTkLabel(dialog, text=field, font=config.FONT_SMALL).pack(
                anchor="w", padx=24, pady=(12, 2))
            entry = ctk.CTkEntry(dialog, height=34, font=config.FONT_NORMAL)
            entry.insert(0, value)
            entry.pack(fill="x", padx=24)
            entries[field] = entry

        note = ("New customers start as Regular Members (10% discount)."
                if customer is None else
                "Tier changes automatically with points -- it can't be edited.")
        ctk.CTkLabel(dialog, text=note, font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, wraplength=310).pack(padx=24, pady=8)

        def save():
            try:
                if customer is None:
                    customer_service.register_customer(
                        entries["Name"].get(), entries["Phone"].get(), entries["Email"].get())
                else:
                    customer_service.update_customer(
                        customer, entries["Name"].get(), entries["Phone"].get(), entries["Email"].get())
            except ValueError as error:
                messagebox.showwarning("Check Input", str(error), parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(dialog, text="Save", height=38, fg_color=config.PRIMARY,
                      hover_color=config.PRIMARY_HOVER, font=config.FONT_NORMAL,
                      command=save).pack(fill="x", padx=24, pady=12)

    def show_history(self, customer):
        history = booking_service.booking_history_for(customer)
        if not history:
            messagebox.showinfo("Booking History",
                                f"{customer.name} has no bookings yet.")
            return
        lines = [f"{b.booking_id}  {b.screening.movie.title}  "
                 f"({len(b.screening_seats)} seats)  ${b.final_amount:.2f}"
                 for b in history]
        messagebox.showinfo(f"Booking History - {customer.name}", "\n".join(lines))

    def on_show(self):
        super().on_show()
        self.refresh()
