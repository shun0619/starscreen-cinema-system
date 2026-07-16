"""
Business Logic - Customers  [Member 2]
Validation + search/filter rules. Screens never touch the data directly.
"""
from data_access import customer_repository
from models.customer import Customer, REGISTERED_TIERS, TIERS


def list_customers(search="", tier_filter="All"):
    search = (search or "").lower()
    result = []
    for c in customer_repository.get_all():
        if search and search not in c.name.lower() and search not in c.email.lower():
            continue
        if tier_filter not in ("All", "") and c.get_membership_tier() != tier_filter:
            continue
        result.append(c)
    return result


def register_customer(name, phone, email):
    """New customers always start as Regular Members (assignment rule)."""
    name, phone, email = (name or "").strip(), (phone or "").strip(), (email or "").strip()
    if not name or not email:
        raise ValueError("Name and email are required.")
    customer = Customer(customer_repository.next_id(), name, phone, email)
    customer_repository.add(customer)
    return customer


def update_customer(customer, name, phone, email):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required.")
    customer.name, customer.phone, customer.email = name, (phone or "").strip(), (email or "").strip()
    customer_repository.save(customer)   # write-through to SQL Server
    return customer


def get_tier_names():
    return [t.tier_name for t in REGISTERED_TIERS]


def get_tier_badge(tier_name):
    for t in TIERS:
        if t.tier_name == tier_name:
            return t.badge
    return ("#e2e8f0", "#334155")
