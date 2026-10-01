import os

# Must run BEFORE the app is imported, so tests use in-memory SQLite
# and never create the real equiptrack.db file.
os.environ["DATABASE_URL"] = "sqlite://"
