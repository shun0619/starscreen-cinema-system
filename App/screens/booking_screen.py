"""
==========================================
[Member 4] New Booking screen
==========================================
The full booking flow on one screen:
 1. choose a screening (its own seat map loads)
 2. look up the customer (their tier + points appear -- discount is automatic)
 3. click seats (the price breakdown updates live: subtotal / discount / GST / total)
 4. choose payment (Cash asks for the amount and shows change due)
 5. Confirm -> seats turn taken immediately, points update, receipt pops up
"""

import customtkinter as ctk
from tkinter import messagebox

from business_logic import booking_service, customer_service
import config
from widgets.base_screen import BaseScreen
from business_logic import screening_service

SEAT_COLORS = {
    # (fg_color, text_color, border)
    "standard": ("#ffffff", config.TEXT, "#cbd5e1"),
    "premium": ("#fef3c7", "#92400e", "#f59e0b"),
    "selected": (config.PRIMARY, "#ffffff", config.PRIMARY),
    "booked": ("#e2e8f0", "#94a3b8", "#e2e8f0"),
}


class BookingScreen(BaseScreen):

    title = "New Booking"

    def build(self):
        self.screening = None
        self.customer = None
        self.selected = set()      # {(row, number)}
        self.seat_buttons = {}     # {(row, number): CTkButton}

        # ================= LEFT: screening picker + seat map =================
        left = self.card(self.content)
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        picker_row = ctk.CTkFrame(left, fg_color="transparent")
        picker_row.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(picker_row, text="Screening:", font=config.FONT_NORMAL,
                     text_color=config.TEXT).pack(side="left", padx=(0, 8))
        self.screening_menu = ctk.CTkOptionMenu(
            picker_row, values=["-"], command=self.on_screening_change,
            height=34, fg_color=config.PAGE_BG, text_color=config.TEXT,
            button_color=config.PRIMARY, font=config.FONT_SMALL, dynamic_resizing=False)
        self.screening_menu.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(left, text="S C R E E N", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, fg_color="#e2e8f0",
                     corner_radius=6, height=26).pack(fill="x", padx=60, pady=(10, 4))

        # Legend
        legend = ctk.CTkFrame(left, fg_color="transparent")
        legend.pack(pady=(2, 6))
        for label, key in [("Standard", "standard"), ("Premium", "premium"),
                           ("Selected", "selected"), ("Taken", "booked")]:
            bg, fg, border = SEAT_COLORS[key]
            ctk.CTkLabel(legend, text=f" {label} ", fg_color=bg, text_color=fg,
                         corner_radius=6, font=config.FONT_SMALL,
                         height=20).pack(side="left", padx=6)

        self.seat_grid = ctk.CTkFrame(left, fg_color="transparent")
        self.seat_grid.pack(pady=(4, 14))

        # ================= RIGHT: customer + breakdown + payment =================
        right = ctk.CTkFrame(self.content, fg_color="transparent", width=300)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        # ---- Customer lookup ----
        cust_card = self.card(right)
        cust_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(cust_card, text="CUSTOMER", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT).pack(anchor="w", padx=16, pady=(12, 4))
        self.customer_menu = ctk.CTkOptionMenu(
            cust_card, values=["-"], command=self.on_customer_change,
            height=34, fg_color=config.PAGE_BG, text_color=config.TEXT,
            button_color=config.PRIMARY, font=config.FONT_SMALL, dynamic_resizing=False)
        self.customer_menu.pack(fill="x", padx=16)
        self.customer_info = ctk.CTkLabel(cust_card, text="", font=config.FONT_SMALL,
                                          text_color=config.TEXT_LIGHT, anchor="w",
                                          justify="left")
        self.customer_info.pack(fill="x", padx=16, pady=(4, 12))

        # ---- Price breakdown (updates live) ----
        price_card = self.card(right)
        price_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(price_card, text="PRICE BREAKDOWN", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT).pack(anchor="w", padx=16, pady=(12, 6))
        self.breakdown_labels = {}
        for key, caption in [("seats", "Seats"), ("subtotal", "Subtotal"),
                             ("discount", "Discount"), ("gst", f"GST ({config.GST_PERCENT}%)"),
                             ("total", "TOTAL")]:
            row = ctk.CTkFrame(price_card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            bold = key == "total"
            font = config.FONT_HEADING if bold else config.FONT_NORMAL
            ctk.CTkLabel(row, text=caption, font=font,
                         text_color=config.TEXT if bold else config.TEXT_LIGHT
                         ).pack(side="left")
            value = ctk.CTkLabel(row, text="-", font=font, text_color=config.TEXT)
            value.pack(side="right")
            self.breakdown_labels[key] = value
        ctk.CTkFrame(price_card, fg_color="transparent", height=8).pack()

        # ---- Payment ----
        pay_card = self.card(right)
        pay_card.pack(fill="x")
        ctk.CTkLabel(pay_card, text="PAYMENT", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT).pack(anchor="w", padx=16, pady=(12, 6))
        self.payment_method = ctk.CTkSegmentedButton(
            pay_card, values=booking_service.payment_methods(),
            command=self.on_payment_change, height=32, font=config.FONT_SMALL,
            selected_color=config.PRIMARY, selected_hover_color=config.PRIMARY_HOVER)
        self.payment_method.set("Card")
        self.payment_method.pack(fill="x", padx=16)
        self.cash_entry = ctk.CTkEntry(pay_card, placeholder_text="Cash received, e.g. 50.00",
                                       height=34, font=config.FONT_NORMAL)
        # (cash_entry only packs when Cash is selected)

        ctk.CTkButton(pay_card, text="Confirm Booking", height=42,
                      fg_color=config.SUCCESS, hover_color="#15803d",
                      font=config.FONT_NORMAL,
                      command=self.confirm).pack(fill="x", padx=16, pady=14)

    # ------------------------------------------------------------------
    # Dropdown data + change handlers
    # ------------------------------------------------------------------
    def reload_options(self):
        self.screenings = screening_service.list_active_screenings()
        labels = [s.label for s in self.screenings] or ["-"]
        self.screening_menu.configure(values=labels)

        prefill = getattr(self.controller, "prefill_screening", None)
        target = prefill if prefill in self.screenings else self.screenings[0] if self.screenings else None
        self.controller.prefill_screening = None
        if target:
            self.screening_menu.set(target.label)
            self.on_screening_change(target.label)

        self.customers = customer_service.list_customers()
        names = ["Guest (walk-in)"] + [c.name for c in self.customers]
        self.customer_menu.configure(values=names)
        self.customer_menu.set(names[0])
        self.on_customer_change(names[0])

    def on_screening_change(self, label):
        self.screening = screening_service.find_by_label(label)
        self.selected.clear()
        self.rebuild_seat_map()
        self.update_breakdown()

    def on_customer_change(self, name):
        if name == "Guest (walk-in)":
            self.customer = booking_service.make_guest()
        else:
            self.customer = next((c for c in self.customers if c.name == name), None)
        if self.customer:
            tier = self.customer.get_membership_tier()
            pct = int(self.customer.tier.discount_rate * 100)
            self.customer_info.configure(
                text=f"Tier: {tier} ({pct}% discount)\nPoints: {self.customer.points:,}")
        self.update_breakdown()

    def on_payment_change(self, method):
        if method == "Cash":
            self.cash_entry.pack(fill="x", padx=16, pady=(8, 0))
        else:
            self.cash_entry.pack_forget()

    # ------------------------------------------------------------------
    # Seat map
    # ------------------------------------------------------------------
    def rebuild_seat_map(self):
        for widget in self.seat_grid.winfo_children():
            widget.destroy()
        self.seat_buttons.clear()
        if self.screening is None:
            return

        # One grid: row labels + seat buttons, always aligned.
        seen_rows = []
        for (row, number), ss in sorted(self.screening.seat_map.items()):
            if row not in seen_rows:
                seen_rows.append(row)
                ctk.CTkLabel(self.seat_grid, text=row, font=config.FONT_SMALL,
                             text_color=config.TEXT_LIGHT, width=20).grid(
                    row=len(seen_rows) - 1, column=0, padx=(0, 6))
            r = seen_rows.index(row)
            btn = ctk.CTkButton(
                self.seat_grid, text=str(number), width=40, height=32,
                corner_radius=6, border_width=1, font=config.FONT_SMALL,
                command=lambda k=(row, number): self.toggle_seat(k))
            btn.grid(row=r, column=number, padx=2, pady=2)
            self.seat_buttons[(row, number)] = btn
            self.paint_seat((row, number))

    def paint_seat(self, key):
        ss = self.screening.seat_map[key]
        btn = self.seat_buttons[key]
        if ss.is_booked:
            state_key, state = "booked", "disabled"
        elif key in self.selected:
            state_key, state = "selected", "normal"
        else:
            state_key, state = ("premium" if ss.seat.is_premium else "standard"), "normal"
        bg, fg, border = SEAT_COLORS[state_key]
        btn.configure(fg_color=bg, text_color=fg, border_color=border,
                      hover_color=bg if state == "disabled" else config.PRIMARY_HOVER,
                      state=state)

    def toggle_seat(self, key):
        if key in self.selected:
            self.selected.remove(key)
        else:
            self.selected.add(key)
        self.paint_seat(key)
        self.update_breakdown()

    # ------------------------------------------------------------------
    # Price breakdown + confirm
    # ------------------------------------------------------------------
    def update_breakdown(self):
        if not (self.screening and self.customer and self.selected):
            for key in self.breakdown_labels:
                self.breakdown_labels[key].configure(text="-")
            return
        p = booking_service.price_preview(self.customer, self.screening, self.selected)
        seat_codes = ", ".join(f"{r}{n}" for r, n in sorted(self.selected))
        self.breakdown_labels["seats"].configure(text=seat_codes)
        self.breakdown_labels["subtotal"].configure(text=f"${p['subtotal']:.2f}")
        self.breakdown_labels["discount"].configure(text=f"-${p['discount']:.2f}")
        self.breakdown_labels["gst"].configure(text=f"+${p['gst']:.2f}")
        self.breakdown_labels["total"].configure(text=f"${p['total']:.2f}")

    def confirm(self):
        try:
            booking, payment, receipt_text = booking_service.confirm_booking(
                self.controller.current_user, self.customer, self.screening,
                set(self.selected), self.payment_method.get(),
                self.cash_entry.get())
        except (ValueError, PermissionError) as error:
            messagebox.showwarning("Cannot Complete Booking", str(error))
            return

        # Booked seats now show as taken immediately (assignment rule)
        for key in list(self.selected):
            self.selected.discard(key)
            self.paint_seat(key)
        self.update_breakdown()
        self.on_customer_change(self.customer_menu.get())  # refresh points display
        self.show_receipt(receipt_text)

    def show_receipt(self, receipt_text):
        popup = ctk.CTkToplevel(self)
        popup.title("Receipt")
        popup.geometry("420x560")
        popup.transient(self.winfo_toplevel())
        box = ctk.CTkTextbox(popup, font=("Courier New", 12))
        box.pack(fill="both", expand=True, padx=14, pady=14)
        box.insert("1.0", receipt_text)
        box.configure(state="disabled")

    def on_show(self):
        super().on_show()
        self.reload_options()
