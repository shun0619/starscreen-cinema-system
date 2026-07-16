"""
==========================================
[Member 5] Reports screen (Managers only)
==========================================
Four live business reports, generated polymorphically from the Report
class hierarchy (report_service returns whatever each subclass's
generate() produces -- this screen never hard-codes a number):

  1. Daily revenue by membership tier   (RevenueReport)      -> bar chart card
  2. Top movies by tickets sold         (TopMoviesReport)     -> horizontal bar chart card
  3. Membership distribution            (MembershipDistributionReport) -> donut + native legend
  4. Seat occupancy per screen          (SeatOccupancyReport) -> native colored progress bars

Charts use small matplotlib figures embedded in their own card (with a
native CTk header above them, like the rest of the app); the donut's
legend and the occupancy bars are built natively so they stay crisp and
themeable instead of being baked into the chart image.
"""

import customtkinter as ctk
from tkinter import messagebox

import config
from widgets.base_screen import BaseScreen
from business_logic import report_service

TIER_COLORS = {"Guest": "#94a3b8", "Regular": "#3b82f6",
               "Silver": "#64748b", "Gold": "#f59e0b"}

STAT_CARDS = [
    ("revenue", "\u2197", "#dbeafe", "#2563eb", "WEEKLY REVENUE"),
    ("bookings", "\U0001F39F", "#dcfce7", "#16a34a", "TOTAL BOOKINGS"),
    ("avg_ticket", "$", "#fef3c7", "#d97706", "AVG TICKET PRICE"),
    ("customers", "\U0001F465", "#ede9fe", "#7c3aed", "TOTAL MEMBERS"),
]


class ReportsScreen(BaseScreen):

    title = "Reports"

    def build(self):
        # ---- Row 0: icon stat cards ----
        cards_row = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, 14))
        self.stat_value_labels = {}
        self.stat_sub_labels = {}
        for key, icon, icon_bg, icon_fg, caption in STAT_CARDS:
            card = self.card(cards_row)
            card.pack(side="left", expand=True, fill="both", padx=6)

            icon_box = ctk.CTkLabel(card, text=icon, width=40, height=40,
                                    corner_radius=10, fg_color=icon_bg,
                                    text_color=icon_fg, font=("Segoe UI", 16, "bold"))
            icon_box.pack(anchor="w", padx=16, pady=(14, 6))

            value = ctk.CTkLabel(card, text="-", font=("Segoe UI", 22, "bold"),
                                 text_color=config.TEXT, anchor="w")
            value.pack(anchor="w", padx=16)
            ctk.CTkLabel(card, text=caption, font=config.FONT_SMALL,
                         text_color=config.TEXT_LIGHT, anchor="w").pack(
                anchor="w", padx=16, pady=(2, 0))
            sub = ctk.CTkLabel(card, text="", font=config.FONT_SMALL,
                               text_color=config.TEXT_LIGHT, anchor="w")
            sub.pack(anchor="w", padx=16, pady=(0, 14))
            self.stat_value_labels[key] = value
            self.stat_sub_labels[key] = sub

        # ---- Row 1: daily revenue + top movies ----
        row1 = ctk.CTkFrame(self.content, fg_color="transparent")
        row1.pack(fill="both", expand=True, pady=(0, 14))
        self.revenue_card, self.revenue_chart_slot = self._chart_card(
            row1, "DAILY REVENUE \u2014 THIS WEEK", side="left", padx=(0, 7))
        self.movies_card, self.movies_chart_slot = self._chart_card(
            row1, "TOP MOVIES THIS WEEK", side="left", padx=(7, 0))

        # ---- Row 2: membership donut + seat occupancy ----
        row2 = ctk.CTkFrame(self.content, fg_color="transparent")
        row2.pack(fill="both", expand=True)

        member_card = self.card(row2)
        member_card.pack(side="left", fill="both", expand=True, padx=(0, 7))
        ctk.CTkLabel(member_card, text="MEMBERSHIP DISTRIBUTION", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, anchor="w").pack(
            fill="x", padx=16, pady=(14, 6))
        member_body = ctk.CTkFrame(member_card, fg_color="transparent")
        member_body.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.donut_slot = ctk.CTkFrame(member_body, fg_color="transparent", width=170)
        self.donut_slot.pack(side="left", fill="y")
        self.legend_box = ctk.CTkFrame(member_body, fg_color="transparent")
        self.legend_box.pack(side="left", fill="both", expand=True, padx=(14, 0))

        occ_card = self.card(row2)
        occ_card.pack(side="left", fill="both", expand=True, padx=(7, 0))
        ctk.CTkLabel(occ_card, text="SEAT OCCUPANCY BY SCREEN", font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, anchor="w").pack(
            fill="x", padx=16, pady=(14, 10))
        self.occupancy_box = ctk.CTkFrame(occ_card, fg_color="transparent")
        self.occupancy_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.canvas_widgets = []

    def _chart_card(self, parent, header_text, side, padx):
        card = self.card(parent)
        card.pack(side=side, fill="both", expand=True, padx=padx)
        ctk.CTkLabel(card, text=header_text, font=config.FONT_SMALL,
                     text_color=config.TEXT_LIGHT, anchor="w").pack(
            fill="x", padx=16, pady=(14, 6))
        slot = ctk.CTkFrame(card, fg_color="transparent")
        slot.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        return card, slot

    # ------------------------------------------------------------------
    def refresh(self):
        try:
            reports = report_service.generate_all_reports(self.controller.current_user)
        except PermissionError as error:
            messagebox.showwarning("Access Denied", str(error))
            self.controller.show_frame("DashboardScreen")
            return

        stats = report_service.dashboard_stats()
        avg_ticket = stats["revenue"] / stats["tickets"] if stats["tickets"] else 0
        self.stat_value_labels["revenue"].configure(text=f"${stats['revenue']:,.2f}")
        self.stat_value_labels["bookings"].configure(text=f"{stats['bookings']:,}")
        self.stat_value_labels["avg_ticket"].configure(text=f"${avg_ticket:,.2f}")
        self.stat_value_labels["customers"].configure(text=f"{stats['customers']:,}")
        self.stat_sub_labels["bookings"].configure(text="This week")
        self.stat_sub_labels["avg_ticket"].configure(text="After discounts")
        self.stat_sub_labels["customers"].configure(text="Registered members")

        revenue, top_movies, occupancy, membership = reports
        self.stat_sub_labels["revenue"].configure(
            text=f"Total across {stats['bookings']} bookings")

        try:
            self._draw_revenue_chart(revenue)
            self._draw_top_movies_chart(top_movies)
            self._draw_donut(membership)
        except Exception as error:  # matplotlib missing/broken must not crash the app
            messagebox.showerror(
                "Charts Unavailable",
                f"Could not draw the report charts:\n{error}\n\n"
                "Check that matplotlib is installed (pip install -r requirements.txt).")

        self._draw_occupancy_bars(occupancy)

    # ------------------------------------------------------------------
    def _new_figure(self, figsize):
        from matplotlib.figure import Figure
        fig = Figure(figsize=figsize, dpi=100, facecolor="none")
        return fig

    def _embed(self, fig, slot):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        for widget in slot.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=slot)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=config.CARD_BG, highlightthickness=0)
        widget.pack(fill="both", expand=True)
        self.canvas_widgets.append(widget)

    def _style_axes(self, ax):
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=9, colors=config.TEXT_LIGHT)
        ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
        ax.set_axisbelow(True)

    def _draw_revenue_chart(self, revenue):
        fig = self._new_figure((5.6, 3.0))
        ax = fig.add_subplot(111)
        tiers = list(revenue["revenue_by_tier"].keys())
        values = list(revenue["revenue_by_tier"].values())
        bars = ax.bar(tiers, values, color=[TIER_COLORS.get(t, config.PRIMARY) for t in tiers],
                      width=0.55)
        for b in bars:
            h = b.get_height()
            ax.annotate(f"${h:,.0f}", (b.get_x() + b.get_width() / 2, h),
                       ha="center", va="bottom", fontsize=8, color=config.TEXT_LIGHT)
        self._style_axes(ax)
        ax.set_ylabel("Revenue ($)", fontsize=9, color=config.TEXT_LIGHT)
        fig.tight_layout(pad=1.2)
        self._embed(fig, self.revenue_chart_slot)

    def _draw_top_movies_chart(self, top_movies):
        fig = self._new_figure((5.6, 3.0))
        ax = fig.add_subplot(111)
        titles = [t for t, _ in top_movies["top_movies"]][::-1]
        tickets = [n for _, n in top_movies["top_movies"]][::-1]
        ax.barh(titles, tickets, color=config.SIDEBAR_BG, height=0.55)
        for i, v in enumerate(tickets):
            ax.annotate(str(v), (v, i), va="center", ha="left",
                       fontsize=8, color=config.TEXT_LIGHT, xytext=(4, 0),
                       textcoords="offset points")
        self._style_axes(ax)
        ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
        ax.set_xlabel("Tickets sold", fontsize=9, color=config.TEXT_LIGHT)
        fig.tight_layout(pad=1.2)
        self._embed(fig, self.movies_chart_slot)

    def _draw_donut(self, membership):
        fig = self._new_figure((2.2, 2.2))
        ax = fig.add_subplot(111)
        counts = list(membership["counts"].values())
        colors = [TIER_COLORS.get(t, config.PRIMARY) for t in membership["counts"]]
        ax.pie(counts, colors=colors, startangle=90,
              wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2})
        ax.set_aspect("equal")
        fig.tight_layout(pad=0.2)
        self._embed(fig, self.donut_slot)

        for widget in self.legend_box.winfo_children():
            widget.destroy()
        for tier, count in membership["counts"].items():
            row = ctk.CTkFrame(self.legend_box, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text="  ", width=14, height=14, corner_radius=4,
                        fg_color=TIER_COLORS.get(tier, config.PRIMARY)).pack(side="left")
            ctk.CTkLabel(row, text=tier, font=config.FONT_NORMAL,
                        text_color=config.TEXT, anchor="w", width=90).pack(
                side="left", padx=(8, 0))
            ctk.CTkLabel(row, text=str(count), font=("Segoe UI", 13, "bold"),
                        text_color=config.TEXT).pack(side="right")
        ctk.CTkLabel(self.legend_box, text=f"Total: {membership['total']} members",
                    font=config.FONT_SMALL, text_color=config.TEXT_LIGHT,
                    anchor="w").pack(fill="x", pady=(10, 0))

    def _draw_occupancy_bars(self, occupancy):
        for widget in self.occupancy_box.winfo_children():
            widget.destroy()
        for screen, pct in occupancy["occupancy"].items():
            color = ("#dc2626" if pct >= 80 else "#f59e0b" if pct >= 50 else config.SUCCESS)
            row = ctk.CTkFrame(self.occupancy_box, fg_color="transparent")
            row.pack(fill="x", pady=8)

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=screen, font=config.FONT_NORMAL,
                        text_color=config.TEXT, anchor="w").pack(side="left")
            ctk.CTkLabel(top, text=f"{pct}%", font=("Segoe UI", 13, "bold"),
                        text_color=color).pack(side="right")

            bar = ctk.CTkProgressBar(row, height=10, corner_radius=5,
                                     progress_color=color, fg_color="#e5e7eb")
            bar.set(pct / 100)
            bar.pack(fill="x", pady=(6, 0))

    def on_show(self):
        super().on_show()
        self.refresh()
