"""
M2 - Customers & membership.

TC-02: earning points past 500 auto-upgrades a Regular member to Silver
and raises the discount rate -- staff never change tiers by hand.
"""

from models.customer import Customer, REGULAR, SILVER


def test_points_trigger_tier_upgrade():
    customer = Customer("CU-TEST", "Test User", "", "t@example.com", 450, REGULAR)

    old_tier, new_tier = customer.update_points(60)  # +60 pts -> 510 total

    assert old_tier is REGULAR
    assert new_tier is SILVER
    assert customer.points == 510
    assert customer.tier.discount_rate == 0.20
