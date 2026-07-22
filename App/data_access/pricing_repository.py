"""
Data Access - Pricing lookup  [M4]
"""
from store import PRICING, get_price


def get_all():
    return PRICING


def price_for(screening_type, seat_type):
    return get_price(screening_type, seat_type)
