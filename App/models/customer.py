"""
==========================================
Domain Model - Customer & MembershipTier  [Member 2]
==========================================
Implements the assignment's membership table:

  Guest    no discount   no points
  Regular  10% off       1.0 pt/$   -> Silver at 500 points
  Silver   20% off       1.5 pt/$   -> Gold at 1,000 points
  Gold     30% off       2.0 pt/$   (highest tier)

Upgrades happen automatically inside update_points() -- staff never
change a tier by hand.
"""


class MembershipTier:

    def __init__(self, tier_id, tier_name, discount_rate, points_per_dollar,
                 upgrade_threshold=None, badge=("#e2e8f0", "#334155")):
        self.tier_id = tier_id
        self.tier_name = tier_name
        self.discount_rate = discount_rate          # e.g. 0.10 = 10% off
        self.points_per_dollar = points_per_dollar
        self.upgrade_threshold = upgrade_threshold  # points needed to leave this tier (None = top/none)
        self.badge = badge                          # (bg color, text color) for UI badges

    def calculate_discount(self, amount):
        return round(amount * self.discount_rate, 2)


# The four tiers, ordered lowest -> highest. GUEST is index 0 and is only
# used for unregistered walk-ins; registered customers start at REGULAR.
GUEST = MembershipTier(0, "Guest", 0.00, 0.0, None, ("#f1f5f9", "#64748b"))
REGULAR = MembershipTier(1, "Regular", 0.10, 1.0, 500, ("#dbeafe", "#1d4ed8"))
SILVER = MembershipTier(2, "Silver", 0.20, 1.5, 1000, ("#e2e8f0", "#334155"))
GOLD = MembershipTier(3, "Gold", 0.30, 2.0, None, ("#fef3c7", "#92400e"))

TIERS = [GUEST, REGULAR, SILVER, GOLD]
REGISTERED_TIERS = [REGULAR, SILVER, GOLD]


def tier_for_points(points):
    """Which registered tier a points balance corresponds to."""
    if points >= 1000:
        return GOLD
    if points >= 500:
        return SILVER
    return REGULAR


class Customer:

    def __init__(self, customer_id, name, phone, email, points=0, tier=None):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.points = points
        # New registered customers start as Regular Members (assignment rule)
        self.tier = tier if tier is not None else REGULAR

    def get_membership_tier(self):
        return self.tier.tier_name

    def update_points(self, amount_spent):
        """Earn points on a purchase, then auto-upgrade if a threshold is
        crossed. Returns (old_tier, new_tier) so callers can record the
        change in the membership history."""
        old_tier = self.tier
        self.points += int(round(amount_spent * self.tier.points_per_dollar))
        if self.tier is not GUEST:  # guests never earn points or upgrade
            self.tier = tier_for_points(self.points)
        return old_tier, self.tier
