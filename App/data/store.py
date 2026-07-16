"""
==========================================
Data store facade  [M5]
==========================================
The ONLY place that decides where the app's data comes from:

  - SQL Server (data_access/db_loader.py) when .env has DB_ENABLED=true
    and the database is reachable, or
  - the in-memory sample data (data/sample_data.py) otherwise.

Repositories import their lists from here, so none of them care which
source is active -- and a member without a local SQL Server can still
run and develop the whole app.
"""

from data_access import db

if db.enabled():
    from data_access.db_loader import (
        USERS, GENRES, MOVIES, SCREENS, PRICING, SCREENING_TYPES,
        SCREENINGS, CUSTOMERS, MEMBERSHIP_HISTORY, BOOKINGS, PAYMENTS,
        get_price,
    )
else:
    from data.sample_data import (
        USERS, GENRES, MOVIES, SCREENS, PRICING, SCREENING_TYPES,
        SCREENINGS, CUSTOMERS, MEMBERSHIP_HISTORY, BOOKINGS, PAYMENTS,
        get_price,
    )
