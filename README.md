# StarScreen Cinemas Management System

SOFT605 Group Assignment - a Python desktop app for a 3-screen cinema:
staff login with role-based access, customer membership tiers with
automatic discounts and upgrades, movie/screening catalogue, visual seat
booking with payment and receipts, and live management reports.

## Team & Code Ownership

Ownership is tagged `[M1]`–`[M5]` throughout this README and the code
(e.g. `main.py ... [M1]`). This table maps each tag to its owner.

| Tag | Member | Name | Area |
|-----|--------|--------|------|
| M1 | Member 1 | shun | Login, Roles & Admin |
| M2 | Member 2 | tehan | Customers & Membership |
| M3 | Member 3 | hansc | Movies & Screenings |
| M4 | Member 4 | han | Booking & Payment |
| M5 | Member 5 | shreya | Database & Reports |

---

## Technology Stack

- Python 3.10+
- CustomTkinter (modern Tkinter widgets - rounded corners, hover states)
- Matplotlib (report charts)
- SQL Server via pyodbc (`database/schema.sql`); falls back to in-memory
  sample data when no database is configured
- pytest (automated tests in `App/tests/`)
- GitHub

---

## Architecture

Four layers; the UI never touches raw data directly:

```
screens/          Presentation  -- CustomTkinter UI, handles clicks
      |  calls
business_logic/   Business Logic -- validation, pricing, discounts, role checks
      |  \
      |   \  builds & calls methods on
      |    +----------------> models/   Domain Model -- the classes:
      |                                  Staff->Cashier/Manager,
      |                                  Customer+MembershipTier, Movie, Screen,
      |                                  Screening, Seat, ScreeningSeat, Pricing,
      |                                  Booking+BookingSeat, Payment, Receipt,
      |                                  Report hierarchy (no data-access imports)
      |  reads/writes through
data_access/      Data Access   -- one repository file per entity;
      |                            returns and persists the model objects above
      |  reads/writes through
store.py          Data store facade -- picks the active data source:
      |             SQL Server (data_access/db_loader.py, via db.py + .env)
      |             or in-memory sample data (sampledata/sample_data.py)
```

Business logic depends on **both** `models/` and `data_access/`: it calls
repositories to fetch/persist data and works on the returned domain objects.
`models/` is pure -- it never imports `data_access/` -- so the domain classes
stay independent of where the data is stored.

**Why:** screens and business logic never know where the data lives.
`store.py` loads the objects from SQL Server when `.env` enables it
(each repository then writes changes back to the database), and falls
back to the sample data otherwise -- so a member without SQL Server set
up can still run and develop every feature.

### Where the OOP concepts live (for the report)

- **Abstraction** - `models/staff.py` (`Staff` is abstract) and
  `models/report.py` (`Report` is abstract); neither can be instantiated.
- **Inheritance** - `Cashier`/`Manager` inherit `Staff`; four report types
  inherit `Report`; every screen inherits `widgets/base_screen.py`'s
  `BaseScreen` (shared sidebar + title layout).
- **Polymorphism** - `Staff.get_permissions()` is overridden per role, and
  all access checks call it without ever testing the role name;
  `Report.generate()` is overridden per report and the Reports screen draws
  whatever it receives.
- **Encapsulation** - `Staff._password` is only read inside `login()`;
  tier upgrades happen only inside `Customer.update_points()`; the price
  breakdown is computed only inside `Booking.calculate_total()`.

### Key business rules (from the brief)

- Tiers: Guest 0% / Regular 10% / Silver 20% / Gold 30% discount.
- Points: 1 / 1.5 / 2 per $1; auto-upgrade at 500 (Silver) and 1,000 (Gold)
  points -- recorded in the membership history. Staff never edit tiers.
- Price = seat-type x screening-type lookup (`models/pricing.py`), minus the
  tier discount, plus 15% GST. The breakdown shows before payment.
- Payments: Cash (shows change due), Card, Voucher. A receipt with the full
  itemised breakdown is generated after every booking.
- Cashiers can book; Managers additionally manage the catalogue and view
  reports. Restricted screens show a clear "access denied" message.

## Project Structure

```
starscreen_cinema/
├── README.md                    # this file
├── classDiagram.mmd              # class diagram (source for the Visio version)
├── ERDiagram.mmd                 # ER diagram (source for the Visio version)
├── ActivityDiagram.mmd           # booking activity diagram
├── UseCaseDiagram.mmd            # use-case diagram
├── ModuleStructureDiagram.mmd    # module / layer structure diagram
├── TestCases.md                  # written test-case table (5 cases)
├── .env.example                  # copy to .env, edit for YOUR SQL Server
├── meeting/                      # meeting notes -> Appendix B minutes
└── App/                          # ALL application code (zip this folder
    │                             #   as GroupName_SOFT605_A1_Code)
    ├── main.py                   # entry point + screen switching   [M1]
    ├── config.py                  # shared colors/fonts/constants    [shared]
    ├── requirements.txt
    ├── store.py                    # data source facade (DB or sample)  [M5]
    ├── database/
    │   ├── db.py                   # .env + SQL Server connection      [shared]
    │   └── schema.sql              # creates all tables + realistic test data [M5]
    ├── sampledata/
    │   └── sample_data.py          # builds all in-memory objects       [M5]
    ├── models/
    │   ├── staff.py                # Staff (abstract) -> Cashier, Manager  [M1]
    │   ├── customer.py             # Customer, MembershipTier + tiers      [M2]
    │   ├── movie.py                # Movie                                  [M3]
    │   ├── screening.py            # Screen, Screening (own seat map)       [M3]
    │   ├── seat.py                 # Seat, ScreeningSeat                    [M4]
    │   ├── pricing.py              # Pricing lookup                         [M4]
    │   ├── booking.py              # Booking + BookingSeat (price breakdown) [M4]
    │   ├── payment.py              # Payment (cash change due)              [M4]
    │   ├── receipt.py              # Receipt text generation                [M4]
    │   └── report.py               # Report (abstract) + 4 report types     [M5]
    ├── data_access/
    │   ├── db_loader.py            [M5]  rebuilds model objects from DB rows
    │   ├── user_repository.py      [M1]
    │   ├── customer_repository.py  [M2]  (+ membership history)
    │   ├── movie_repository.py     [M3]
    │   ├── screening_repository.py [M3]
    │   ├── pricing_repository.py   [M4]
    │   └── booking_repository.py   [M4]  (+ payments, booking transaction)
    ├── business_logic/
    │   ├── auth_service.py         [M1]  login + require_permission
    │   ├── customer_service.py     [M2]
    │   ├── movie_service.py        [M3]
    │   ├── screening_service.py    [M3]  list + add/edit screenings (Manager)
    │   ├── booking_service.py      [M4]  price preview + confirm + receipt
    │   └── report_service.py       [M5]  dashboard stats + 4 live reports
    ├── widgets/                   [shared - ask team before editing]
    │   ├── base_screen.py          # sidebar+title layout all screens inherit
    │   ├── sidebar.py              # nav menu w/ permission checks + user name
    │   └── table.py                # DataTable: one-grid tables (no column drift)
    ├── tests/                     # pytest suite -- one file per role
    │   ├── conftest.py             # makes App/ importable for the tests
    │   ├── test_m1_login.py        # [M1] login + role permissions
    │   ├── test_m2_membership.py   # [M2] points auto-upgrade
    │   ├── test_m3_movies.py       # [M3] manager adds a movie
    │   ├── test_m4_booking.py      # [M4] price breakdown (discount + GST)
    │   └── test_m5_reports.py      # [M5] membership distribution report
    └── screens/
        ├── login_screen.py         [M1]
        ├── dashboard_screen.py     [M1]
        ├── customers_screen.py     [M2]
        ├── movies_screen.py        [M3]
        ├── screenings_screen.py    [M3]
        ├── booking_screen.py       [M4]
        ├── admin_screen.py         [M1]
        └── reports_screen.py       [M5]
```

Each member owns a full vertical slice (screen + service + model +
repository), which maps directly onto the Individual Code Ownership
Declaration in Appendix A.

### Rules for adding or editing a screen

1. New screens go in `screens/` and inherit `BaseScreen`:
   set a `title`, build widgets in `build()` inside `self.content`, and
   refresh data in `on_show()` (call `super().on_show()` first).
2. Register the new screen in `main.py` (`SCREEN_CLASSES`) and add a menu
   entry in `widgets/sidebar.py` (`MENU_ITEMS`), with a permission string
   if it should be Manager-only.
3. Screens call `business_logic/` functions only -- never import from
   `data_access/`, `store.py`, or `sampledata/` directly.
4. Validation and role checks live in `business_logic/`, which raises
   `ValueError` / `PermissionError` with a clear message; the screen catches
   it and shows a message box. The app must never crash with a raw error.
5. Tables must use `widgets/table.py`'s `DataTable` -- it keeps every column
   aligned because header and cells share one grid.

---

## Branch Strategy

Do not commit directly to the `main` branch.

Each team member must work on their own feature branch.

```text
main
├── feature-login
├── feature-customer
├── feature-movie
├── feature-booking
└── feature-reports
```

## Before Starting Work

```bash
git checkout main
git pull origin main
git checkout feature-login   # your branch
git merge main
```

## Save and Push Your Work

```bash
git add .
git commit -m "Describe your changes"
git push origin feature-login
```

## Pull Request

1. Open GitHub -> Pull Requests -> New Pull Request.
2. Base: `main`, Compare: your feature branch.
3. Create the Pull Request; the Team Leader reviews and merges.

## Rules

✅ Pull latest changes before starting work

✅ Work only on your own feature branch

✅ Push changes regularly

✅ Create a Pull Request before merging

❌ Do NOT push directly to `main`

❌ Do NOT edit another member's feature branch

---

## Project Setup

```bash
cd App
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Demo accounts:
- cashier / cashier123  (bookings only)
- manager / manager123  (bookings + catalogue + reports)

---

## Database Setup (SQL Server) -- do this once, on YOUR machine

Every member runs their **own local SQL Server** -- there is no shared
database, so nobody can break anyone else's data. Your personal
connection settings live in `.env`, which is **gitignored**: it never
gets committed, so there are no merge conflicts over server names.

### 1. Create the database

Open `App/database/schema.sql` in SSMS and press **Execute (F5)** -- or
from a terminal (at the repository root):

```bash
sqlcmd -S localhost\SQLEXPRESS -E -i App\database\schema.sql
```

The script creates the `StarScreenCinema` database, all 14 tables, and
realistic test data (customers in every tier, movies in all six genres,
and completed bookings that demonstrate the discount + auto-upgrade
logic). It is **re-runnable**: executing it again resets the database
to a clean state -- handy after testing bookings.

### 2. Point the app at your database

```bash
copy .env.example .env       # then edit .env
```

The `.env` may sit at the repository root (next to `.env.example`) or
inside `App/` -- the app checks both places.

Set `DB_ENABLED=true` and set `DB_SERVER` to the **same "Server name"
you type in SSMS's Connect to Server dialog** -- e.g. your PC name
(`DESKTOP-XXXXXX`) for a default instance, or `localhost\SQLEXPRESS`
for Express. Windows Authentication (no username/password, like in
SSMS) is the default; only if your server uses a SQL login set
`DB_TRUSTED=no` and fill in `DB_USER` / `DB_PASSWORD`.

Rules:

✅ Commit changes to `.env.example` and `database/schema.sql`

❌ Never commit `.env` (it is in .gitignore -- leave it there)

### 3. Run the app

```bash
cd App
python main.py
```

The console prints which data source is active:

- `[db] Connected to SQL Server: ...` -- you are on the database.
- `[db] Could not connect ... -> using sample data.` -- the app still
  runs on the in-memory sample data, so you can keep developing while
  you fix the connection (or before you have installed SQL Server).

### How the database layer is split across the team

- `database/db.py` [shared] -- reads `.env`, opens connections.
- `data_access/db_loader.py` [M5] -- turns rows into the model objects.
- `store.py` [M5] -- picks DB or sample data at startup.
- Each repository [M1-M4] owns the SQL for its own tables: it reads
  from the loaded objects and **writes through** to the database on
  every change (e.g. `booking_repository.persist_confirmed()` saves a
  booking, its seats, the payment, the receipt, and the customer's new
  points in one transaction).
- `database/schema.sql` [M5 coordinates] -- each member writes the
  CREATE TABLE + INSERTs for their own tables (owners are commented in
  the file) so the test data always matches their feature.
  
---

## Testing

The project ships with a small automated test suite -- **one test per
ownership area (M1-M5)**, so every member has a test covering the core
rule of their own feature. All tests run on the in-memory sample data, so
**no SQL Server is required**.

```bash
cd App
python -m pytest tests -v
```

You should see `5 passed`. What each test checks:

| File | Owner | What it verifies |
|---|---|---|
| `tests/test_m1_login.py` | M1 | Login works and permissions follow the role (Manager sees reports, Cashier does not) |
| `tests/test_m2_membership.py` | M2 | Passing 500 points auto-upgrades a Regular member to Silver |
| `tests/test_m3_movies.py` | M3 | A Manager can add a movie to the catalogue |
| `tests/test_m4_booking.py` | M4 | Price = subtotal - tier discount + 15% GST |
| `tests/test_m5_reports.py` | M5 | The membership distribution report counts customers per tier |

The matching written test-case table (for the report) is `TestCases.md` at the repository root.
