"""
==========================================
Database - SQL Server connection  [shared - ask team before editing]
==========================================
Reads connection settings from the .env file at the project root
(copy .env.example to .env and edit it -- .env is gitignored, so every
member points at their OWN local SQL Server without merge conflicts).

If DB_ENABLED is not "true", or pyodbc / the database is unavailable,
enabled() returns False and the whole app silently falls back to the
in-memory sample data (sampledata/sample_data.py). That means members who
haven't installed SQL Server yet can still run and develop the app.
"""

import os

# The .env may live next to the code (App/.env) or one level up at the
# repository root (starscreen_cinema/.env) -- the first one found wins.
_APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_CANDIDATES = [
    os.path.join(_APP_ROOT, ".env"),
    os.path.join(os.path.dirname(_APP_ROOT), ".env"),
]

_env_cache = None      # parsed .env contents
_enabled_cache = None  # result of the one-time connection check


def _env_path():
    for path in _ENV_CANDIDATES:
        if os.path.exists(path):
            return path
    return _ENV_CANDIDATES[0]


def _read_env_file():
    """Tiny .env parser (KEY=value lines, # comments) -- no extra
    dependency needed. Real environment variables take priority."""
    values = {}
    if os.path.exists(_env_path()):
        with open(_env_path(), encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_setting(key, default=""):
    global _env_cache
    if _env_cache is None:
        _env_cache = _read_env_file()
    return os.environ.get(key, _env_cache.get(key, default))


def _detect_driver():
    """Pick the best SQL Server ODBC driver installed on this machine,
    so members don't have to look the name up. DB_DRIVER in .env
    overrides this."""
    try:
        import pyodbc
        drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
        for preferred in ("ODBC Driver 18 for SQL Server",
                          "ODBC Driver 17 for SQL Server"):
            if preferred in drivers:
                return preferred
        if drivers:  # e.g. the legacy "SQL Server" driver Windows ships
            return drivers[-1]
    except ImportError:
        pass
    return "ODBC Driver 17 for SQL Server"


def connection_string():
    driver = get_setting("DB_DRIVER") or _detect_driver()
    server = get_setting("DB_SERVER", r"localhost\SQLEXPRESS")
    database = get_setting("DB_NAME", "StarScreenCinema")
    parts = [f"DRIVER={{{driver}}}", f"SERVER={server}", f"DATABASE={database}"]
    if get_setting("DB_TRUSTED", "yes").lower() in ("yes", "true", "1"):
        parts.append("Trusted_Connection=yes")          # Windows authentication
    else:
        parts.append(f"UID={get_setting('DB_USER')}")   # SQL Server login
        parts.append(f"PWD={get_setting('DB_PASSWORD')}")
    parts.append("TrustServerCertificate=yes")          # needed by ODBC Driver 18
    return ";".join(parts)


def get_connection():
    import pyodbc
    return pyodbc.connect(connection_string(), timeout=5)


def enabled():
    """True only if .env asks for the database AND we can reach it.
    The check runs once; the answer is reused for the whole session."""
    global _enabled_cache
    if _enabled_cache is None:
        _enabled_cache = _check_connection()
    return _enabled_cache


def _check_connection():
    if get_setting("DB_ENABLED", "false").lower() != "true":
        return False
    try:
        import pyodbc  # noqa: F401 -- just checking it is installed
    except ImportError:
        print("[db] DB_ENABLED=true but pyodbc is not installed "
              "(pip install -r requirements.txt) -> using sample data.")
        return False
    try:
        get_connection().close()
        print(f"[db] Connected to SQL Server: {get_setting('DB_SERVER')} / "
              f"{get_setting('DB_NAME', 'StarScreenCinema')}")
        return True
    except Exception as error:
        print(f"[db] Could not connect to SQL Server ({error}) "
              "-> using sample data.")
        return False


# ---- Small helpers so repositories don't repeat cursor code ----

def query(sql, params=()):
    """Run a SELECT and return all rows."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()


def execute(sql, params=()):
    """Run a single INSERT/UPDATE/DELETE and commit."""
    with get_connection() as conn:
        conn.cursor().execute(sql, params)
        conn.commit()


def execute_transaction(statements):
    """Run several (sql, params) statements in ONE transaction --
    either everything is saved or nothing is (used by bookings)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for sql, params in statements:
            cursor.execute(sql, params)
        conn.commit()
