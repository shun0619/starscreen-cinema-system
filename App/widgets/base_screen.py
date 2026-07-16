"""
==========================================
Shared widget - BaseScreen  [shared - ask team before editing]
==========================================
Every screen after login looks the same on the outside: sidebar on the
left, a page title, and a content area. Instead of copy-pasting that
into all seven screens, they all INHERIT from BaseScreen and only build
their own content -- this is inheritance applied to the UI layer.

How to write a new screen:

    class MyScreen(BaseScreen):
        title = "My Page"

        def build(self):
            # add widgets to self.content here
            ...

        def on_show(self):
            super().on_show()   # keeps the sidebar user name fresh
            # refresh your data here
"""

import customtkinter as ctk

import config
from widgets.sidebar import Sidebar


class BaseScreen(ctk.CTkFrame):

    title = "Untitled"

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=config.PAGE_BG, corner_radius=0)
        self.controller = controller

        self.sidebar = Sidebar(self, controller, active_screen=type(self).__name__)
        self.sidebar.pack(side="left", fill="y")

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(side="left", fill="both", expand=True, padx=24, pady=18)

        ctk.CTkLabel(outer, text=self.title, font=config.FONT_TITLE,
                     text_color=config.TEXT, anchor="w").pack(fill="x", pady=(0, 14))

        # Subclasses put all their widgets inside self.content
        self.content = ctk.CTkFrame(outer, fg_color="transparent")
        self.content.pack(fill="both", expand=True)

        self.build()

    def build(self):
        """Overridden by each screen to create its own widgets."""
        raise NotImplementedError

    def on_show(self):
        """Called by main.py every time the screen is brought to front."""
        self.sidebar.refresh_user()

    # ---- small helpers shared by all screens ----
    def card(self, parent=None, **kwargs):
        """A white rounded card, the basic visual container."""
        kwargs.setdefault("fg_color", config.CARD_BG)
        kwargs.setdefault("corner_radius", 10)
        return ctk.CTkFrame(parent or self.content, **kwargs)
