# Test Cases — StarScreen Cinemas (SOFT605)

One test per ownership area (M1–M5), happy path, all runnable on the
in-memory sample data (no SQL Server required).

- **Environment:** Python 3.10, in-memory sample data (`DB_ENABLED` off / not required)
- **How to run:** `cd App` then `python -m pytest tests -v`


| Test ID | Area (owner) | Objective | Preconditions | Input / Steps | Expected result | Actual result | Status |
|---|---|---|---|---|---|---|---|
| TC-01 | M1 Login & roles | Verify role-based access control (polymorphic `get_permissions()`) | Sample users `manager` / `cashier` exist | Log in as `manager/manager123` and `cashier/cashier123`, then query permissions | Manager logs in, `role="Manager"`, has `reports` permission; Cashier does not have `reports` permission | As expected | Pass |
| TC-02 | M2 Membership & points | Verify auto-upgrade from Regular to Silver once points pass 500 | Regular member (450 pts) | Call `update_points(60)` (+60 pts → 510) | Points 510, tier becomes Silver, discount rate updated to 0.20 | As expected | Pass |
| TC-03 | M3 Movies & catalogue | Verify a Manager can add a movie and it appears in the catalogue | Logged in as Manager, catalogue has N movies | `add_movie(manager, "QA Test Feature", "Action", 100, "M")` | Catalogue has N+1 movies; the new movie is `is_active=True` and retrievable by search | As expected | Pass |
| TC-04 | M4 Booking & pricing | Verify the price breakdown (tier discount + 15% GST) is computed correctly | Silver member, two $10 standard seats | Call `Booking.calculate_total()` | Subtotal 20.00, discount 4.00, GST 2.40, total 18.40 | As expected | Pass |
| TC-05 | M5 Reports | Verify the membership distribution report aggregation (`Report.generate()`) | 4 customers: Regular 2, Silver 1, Gold 1 | `MembershipDistributionReport(customers).generate()` | `total=4`, `counts={Regular:2, Silver:1, Gold:1}`, Regular = 50% | As expected | Pass |

