"""
Data Access - Customers & membership history  [M2]
Reads come from the in-memory objects (loaded from SQL Server or the
sample data). Every change is also written through to the database
when it is enabled -- the persist functions are no-ops otherwise.
"""
from store import CUSTOMERS, MEMBERSHIP_HISTORY
from database import db
from models.customer import TIERS


def _tier_id(tier_name):
    for tier in TIERS:
        if tier.tier_name == tier_name:
            return tier.tier_id
    return 1  # Regular


def get_all():
    return CUSTOMERS


def add(customer):
    CUSTOMERS.append(customer)
    if db.enabled():
        db.execute(
            "INSERT INTO CUSTOMER (customer_id, name, phone, email, points, "
            "tier_id) VALUES (?, ?, ?, ?, ?, ?)",
            (customer.customer_id, customer.name, customer.phone,
             customer.email, customer.points, customer.tier.tier_id))


def save(customer):
    """UPDATE after the customer's details, points, or tier change."""
    if db.enabled():
        db.execute(
            "UPDATE CUSTOMER SET name = ?, phone = ?, email = ?, points = ?, "
            "tier_id = ? WHERE customer_id = ?",
            (customer.name, customer.phone, customer.email, customer.points,
             customer.tier.tier_id, customer.customer_id))


def next_id():
    return f"CU-{len(CUSTOMERS) + 1:04d}"


def add_history(customer, old_tier_name, new_tier_name, when):
    MEMBERSHIP_HISTORY.append((customer, old_tier_name, new_tier_name, when))
    if db.enabled():
        db.execute(
            "INSERT INTO MEMBERSHIP_HISTORY (customer_id, old_tier_id, "
            "new_tier_id, changed_at) VALUES (?, ?, ?, GETDATE())",
            (customer.customer_id, _tier_id(old_tier_name),
             _tier_id(new_tier_name)))


def get_history():
    return MEMBERSHIP_HISTORY
