"""
==========================================
Shared config (colors, fonts, window size)
==========================================
Every screen imports these values. Change once, applies everywhere.
Shared file -- tell the team before editing it.
"""

APP_NAME = "StarScreen Cinemas"

# ---- Colors -------------------------------------------------
PRIMARY = "#2f5fdb"        # brand blue (buttons, highlights)
PRIMARY_HOVER = "#2450b8"
SIDEBAR_BG = "#1e293b"     # dark navy sidebar
SIDEBAR_HOVER = "#334155"
PAGE_BG = "#eef1f5"        # light gray page background
CARD_BG = "#ffffff"
TEXT = "#1f2937"
TEXT_LIGHT = "#6b7280"
DANGER = "#dc2626"
SUCCESS = "#16a34a"

# ---- Fonts (family, size, weight) ---------------------------
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 15, "bold")
FONT_NORMAL = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)

# ---- Window -------------------------------------------------
WINDOW_WIDTH = 1240
WINDOW_HEIGHT = 780

# ---- Business constants -------------------------------------
GST_PERCENT = 15  # NZ GST, added after the membership discount
