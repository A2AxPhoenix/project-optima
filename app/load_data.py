from pathlib import Path
import sqlite3
import pandas as pd

from app.db import DB_PATH, create_tables, get_connection

import nflreadpy as nfl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

PLAYERS_CACHE = DATA_DIR / "players_cache.csv"
GAME_LOGS_CACHE = DATA_DIR / "game_logs_cache.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_data():
    """Fetch real NFL data using nflreadpy."""
    print("Fetching live NFL data...")

    players = nfl.load_players()
    stats = nfl.load_player_stats([2023, 2024])

    return players, stats

def save_cache(players_df, stats_df):
    """Save fetched data to local CSV cache."""
    print("Saving cache files...")

    players_df.to_csv(PLAYERS_CACHE, index=False)
    stats_df.to_csv(GAME_LOGS_CACHE, index=False)

def load_cache():
    """Load previously saved CSV cache."""
    print("Loading cached data...")

    players = pd.read_csv(PLAYERS_CACHE)
    stats = pd.read_csv(GAME_LOGS_CACHE)

    return players, stats

def get_data():
    """Try live fetch first, then fall back to cached CSVs."""
    try:
        players, stats = fetch_data()

        # Convert to pandas if needed
        if not isinstance(players, pd.DataFrame):
            players = players.to_pandas()
        if not isinstance(stats, pd.DataFrame):
            stats = stats.to_pandas()

        save_cache(players, stats)
        print("Live data fetch succeeded.")
        return players, stats

    except Exception as e:
        print(f"Live fetch failed: {e}")
        print("Falling back to cached CSV files...")
        return load_cache()

def clean_players(players_df):
    """Keep only the player columns needed for the MVP."""

    players = players_df[["gsis_id", "display_name", "position"]].copy()

    players = players.rename(columns={
        "gsis_id": "player_id",
        "display_name": "name"
    })

    players = players.dropna(subset=["player_id", "name"])
    players = players.drop_duplicates(subset=["player_id"])

    return players

def clean_game_logs(stats_df):
    """Keep only the game log columns needed for the MVP."""

    columns_to_keep = [
        "player_id",
        "player_display_name",
        "position",
        "team",
        "opponent_team",
        "season",
        "week",
        "carries",
        "targets",
        "receptions",
        "rushing_yards",
        "receiving_yards",
        "rushing_tds",
        "receiving_tds",
        "fantasy_points",
    ]

    game_logs = stats_df[columns_to_keep].copy()

    game_logs = game_logs.rename(columns={
        "player_display_name": "name"
    })

    game_logs = game_logs.dropna(subset=["player_id", "name", "season", "week"])

    numeric_columns = [
        "carries",
        "targets",
        "receptions",
        "rushing_yards",
        "receiving_yards",
        "rushing_tds",
        "receiving_tds",
        "fantasy_points",
    ]

    game_logs[numeric_columns] = game_logs[numeric_columns].fillna(0)

    return game_logs

def insert_players(players_df):
    """Insert cleaned player data into the database."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM players")

    players_df.to_sql("players", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

def insert_game_logs(game_logs_df):
    """Insert cleaned game logs into the database."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM game_logs")

    game_logs_df.to_sql("game_logs", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    players, stats = get_data()

    cleaned_players = clean_players(players)
    cleaned_game_logs = clean_game_logs(stats)

    insert_players(cleaned_players)
    insert_game_logs(cleaned_game_logs)

    print("Data successfully loaded into SQLite")
