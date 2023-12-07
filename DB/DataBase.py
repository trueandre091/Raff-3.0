"""Start of create DB!"""

import sqlite3

DB_PATH = "app.db"

def connect_db():
    """Config connection to DataBase"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Create sheets inside the main DataBase"""

    db = connect_db()
    # db = sqlite3.connect(DB_PATH)
    # db.row_factory = sqlite3.Row

    db.cursor().executescript("""CREATE TABLE IF NOT EXISTS guilds (
    id integer PRIMARY KEY,
    count_members integer NOT NULL)
    """)

    db.cursor().executescript("""CREATE TABLE IF NOT EXISTS members(
    id integer NOT NULL,
    SCORES integer NOT NULL)
    """)

    db.commit()
    db.close()

# db = connect_db()
# db = create_db(db)

# C:\Users\andre\Documents\GitHub\Raff-3.0