"""
M5 - Reports & data.

TC-05: the polymorphic Report.generate() counts customers per tier.
"""

from models.customer import Customer, REGULAR, SILVER, GOLD
from models.report import MembershipDistributionReport


def test_membership_distribution_report():
    customers = [
        Customer("C1", "A", "", "a@x.com", 200, REGULAR),
        Customer("C2", "B", "", "b@x.com", 300, REGULAR),
        Customer("C3", "C", "", "c@x.com", 600, SILVER),
        Customer("C4", "D", "", "d@x.com", 1200, GOLD),
    ]

    result = MembershipDistributionReport(customers).generate()

    assert result["total"] == 4
    assert result["counts"] == {"Regular": 2, "Silver": 1, "Gold": 1}
    assert result["percentages"]["Regular"] == 50
