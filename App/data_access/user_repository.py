"""
Data Access - Users  [M1]
The only file that knows where staff accounts are stored. The store
facade (data/store.py) decides whether they came from SQL Server or
the in-memory sample data.
"""
from data.store import USERS


def find_by_username(username):
    return USERS.get(username)
