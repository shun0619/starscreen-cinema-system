"""
Business Logic - Authentication  [Member 1]
"""
from data_access import user_repository


def login(username, password):
    """Return the Cashier/Manager object if credentials are correct, else None."""
    user = user_repository.find_by_username((username or "").strip())
    if user and user.login((password or "").strip()):
        return user
    return None


def require_permission(current_user, permission):
    """Role-based access rule: raises PermissionError with a clear message
    if this staff member lacks the permission. Uses the polymorphic
    get_permissions() -- we never check the role name here."""
    if current_user is None or not current_user.can(permission):
        raise PermissionError(
            "Access denied: this function is only available to Managers.")
