from pathlib import Path
import sqlite3

# Path to the project root (project-optima)
PROJECT_ROOT = Path(__file__).resolve().parents[1] # __file__ means path to this file (db.py)
DB_PATH = PROJECT_ROOT / "storage" / "optima.db" # Set the db path to project-optima/storage/optima.db

DB_PATH.parent.mkdir(parents=True, exist_ok=True) # If it does not exist, make it. If it does, do nothing

def get_connection():
    """Create and return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def create_tables():
    """Create database tables if they do not exist."""

    conn = get_connection()
    cursor = conn.cursor()

    # Players table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
    player_id TEXT PRIMARY KEY,
    name TEXT,
    position TEXT
    )
                   """)

    # Game logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT,
    name TEXT,
    position TEXT,
    team TEXT,
    opponent_team TEXT,
    season INTEGER,
    week INTEGER,
    carries INTEGER,
    targets INTEGER,
    receptions INTEGER,
    rushing_yards INTEGER,
    receiving_yards INTEGER,
    rushing_tds INTEGER,
    receiving_tds INTEGER,
    fantasy_points REAL
    )
                   """)

    # Index for faster player lookups
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_player_logs
    ON game_logs(player_id)
                   """)

    conn.commit()
    conn.close()
