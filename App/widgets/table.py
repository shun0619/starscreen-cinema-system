"""
==========================================
Shared widget - DataTable  [shared - ask team before editing]
==========================================
WHY THIS EXISTS: the old tables packed each row as its own frame with
character-based label widths, so columns drifted out of line under the
headers. This widget puts the header AND every data cell into ONE grid,
so a column is a real grid column -- it can never misalign.

Usage:
    table = DataTable(parent, columns=["NAME", "EMAIL"], weights=[2, 3])
    table.pack(fill="both", expand=True)
    table.set_rows([
        ["Sarah", "sarah@email.com"],
        ["Michael", Badge("Gold", "#fef3c7", "#92400e")],
        ["Emma", Button("Book", command=some_function)],
    ])
"""

import customtkinter as ctk
import config


class Badge:
    """A small colored pill cell (e.g. membership tier, Active status)."""

    def __init__(self, text, bg, fg):
        self.text, self.bg, self.fg = text, bg, fg


class Button:
    """A clickable button cell (e.g. Book / Edit / Delete)."""

    def __init__(self, text, command, color=None, hover=None, width=64):
        self.text, self.command = text, command
        self.color = color or config.PRIMARY
        self.hover = hover or config.PRIMARY_HOVER
        self.width = width


class DataTable(ctk.CTkFrame):

    def __init__(self, parent, columns, weights=None):
        super().__init__(parent, fg_color=config.CARD_BG, corner_radius=10)
        self.columns = columns
        weights = weights or [1] * len(columns)
        self._cells = []  # every widget below the header, for clearing

        for i, (title, weight) in enumerate(zip(columns, weights)):
            self.grid_columnconfigure(i, weight=weight, minsize=70, uniform="col")
            header = ctk.CTkLabel(
                self, text=title, anchor="w", height=34,
                fg_color=config.SIDEBAR_BG, text_color="white",
                font=config.FONT_SMALL, corner_radius=0, padx=10,
            )
            header.grid(row=0, column=i, sticky="nsew")

    def set_rows(self, rows):
        """Replace all data rows. Each row is a list of cells; a cell is a
        plain string, a Badge, or a Button."""
        for widget in self._cells:
            widget.destroy()
        self._cells = []

        for r, row in enumerate(rows, start=1):
            for c, cell in enumerate(row):
                widget = self._make_cell(cell)
                sticky = "w" if isinstance(cell, (Badge, Button)) else "ew"
                widget.grid(row=r, column=c, sticky=sticky, padx=10, pady=5)
                self._cells.append(widget)

    def _make_cell(self, cell):
        if isinstance(cell, Badge):
            return ctk.CTkLabel(self, text=f" {cell.text} ", fg_color=cell.bg,
                                 text_color=cell.fg, corner_radius=8,
                                 font=config.FONT_SMALL, height=22)
        if isinstance(cell, Button):
            return ctk.CTkButton(self, text=cell.text, command=cell.command,
                                  fg_color=cell.color, hover_color=cell.hover,
                                  width=cell.width, height=26,
                                  font=config.FONT_SMALL)
        return ctk.CTkLabel(self, text=str(cell), anchor="w",
                             text_color=config.TEXT, font=config.FONT_NORMAL)
