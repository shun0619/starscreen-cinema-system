"""
M1 - Login, roles & app shell.

TC-01: valid credentials log in, and permissions follow the role via the
polymorphic get_permissions() -- a Manager may view reports, a Cashier
may not.

Run: cd App && python -m pytest tests -v
"""

from business_logic import auth_service


def test_login_returns_role_and_permissions():
    manager = auth_service.login("manager", "manager123")
    cashier = auth_service.login("cashier", "cashier123")

    assert manager is not None and manager.role == "Manager"
    assert manager.can("reports") is True
    assert cashier.can("reports") is False
