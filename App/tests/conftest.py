"""
Makes the App/ package root importable so the tests can use the same
absolute imports the app uses (e.g. `import config`, `from models... `,
`from business_logic import ...`). No SQL Server is required -- the code
falls back to the in-memory sample data.
"""
import os
import sys

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)
