"""
==========================================
[Member 1] Application entry point (main.py)
==========================================
Run with:  python main.py

Stacks every screen inside one CustomTkinter window; show_frame() brings
a screen to the front and calls its on_show() so it can refresh data.
controller.current_user holds the logged-in Cashier/Manager object.

If you add a new screen: import it below AND add it to SCREEN_CLASSES.
"""

import sys
from tkinter import messagebox

try:
    import customtkinter as ctk
except ImportError:
    print("CustomTkinter is not installed. Run:  pip install -r requirements.txt")
    sys.exit(1)

import config
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.customers_screen import CustomersScreen
from screens.movies_screen import MoviesScreen
from screens.screenings_screen import ScreeningsScreen
from screens.booking_screen import BookingScreen
from screens.admin_screen import AdminScreen
from screens.reports_screen import ReportsScreen

SCREEN_CLASSES = (
    LoginScreen,
    DashboardScreen,
    CustomersScreen,
    MoviesScreen,
    ScreeningsScreen,
    BookingScreen,
    AdminScreen,
    ReportsScreen,
)


class StarScreenApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title(f"{config.APP_NAME} - Management System")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(1100, 700)

        self.current_user = None        # Cashier/Manager object after login
        self.prefill_screening = None   # set by Screenings' "Book" button

        container = ctk.CTkFrame(self, fg_color=config.PAGE_BG, corner_radius=0)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for ScreenClass in SCREEN_CLASSES:
            frame = ScreenClass(parent=container, controller=self)
            self.frames[ScreenClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginScreen")

    def show_frame(self, name):
        frame = self.frames[name]
        try:
            if hasattr(frame, "on_show"):
                frame.on_show()
        except Exception as error:
            # The app must never crash with a raw traceback (assignment rule)
            messagebox.showerror("Unexpected Error",
                                 f"Something went wrong loading this screen:\n{error}")
            return
        frame.tkraise()

    def logout(self):
        if self.current_user:
            self.current_user.logout()
        self.current_user = None
        self.show_frame("LoginScreen")


if __name__ == "__main__":
    app = StarScreenApp()
    app.mainloop()
