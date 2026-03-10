import sqlite3
from app.db import DB_PATH

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def get_player_recent_games(player_name, limit=5):
    """Return a player's most recent games."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            season,
            week,
            team,
            opponent_team,
            carries,
            targets,
            receptions,
            rushing_yards,
            receiving_yards,
            rushing_tds,
            receiving_tds,
            fantasy_points
        FROM game_logs
        WHERE name = ?
        ORDER BY season DESC, week DESC
        LIMIT ?
    """, (player_name, limit))

    rows = cursor.fetchall()
    conn.close()

    return rows

def get_player_average(player_name, limit=5):
    """Return a player's average stats over their most recent games."""
    recent_games = get_player_recent_games(player_name, limit)

    if not recent_games:
        return None

    total_games = len(recent_games)

    total_carries = 0
    total_targets = 0
    total_receptions = 0
    total_rushing_yards = 0
    total_receiving_yards = 0
    total_rushing_tds = 0
    total_receiving_tds = 0
    total_fantasy_points = 0

    for game in recent_games:
        total_carries += game[4]
        total_targets += game[5]
        total_receptions += game[6]
        total_rushing_yards += game[7]
        total_receiving_yards += game[8]
        total_rushing_tds += game[9]
        total_receiving_tds += game[10]
        total_fantasy_points += game[11]

    return {
        "name": player_name,
        "games_used": total_games,
        "avg_carries": total_carries / total_games,
        "avg_targets": total_targets / total_games,
        "avg_receptions": total_receptions / total_games,
        "avg_rushing_yards": total_rushing_yards / total_games,
        "avg_receiving_yards": total_receiving_yards / total_games,
        "avg_rushing_tds": total_rushing_tds / total_games,
        "avg_receiving_tds": total_receiving_tds / total_games,
        "avg_fantasy_points": total_fantasy_points / total_games,
    }

def compare_players(player_a, player_b):
    """Compare two players based on recent average performance."""

    avg_a = get_player_average(player_a)
    avg_b = get_player_average(player_b)

    if avg_a is None or avg_b is None:
        return "One or both players not found."

    recommendation = None
    reason = ""

    if avg_a["avg_fantasy_points"] > avg_b["avg_fantasy_points"]:
        recommendation = player_a
        reason = f"{player_a} has higher recent fantasy production."
    else:
        recommendation = player_b
        reason = f"{player_b} has higher recent fantasy production."

    return {
        "player_a": avg_a,
        "player_b": avg_b,
        "recommendation": recommendation,
        "reason": reason
    }

if __name__ == "__main__":
    comparison = compare_players("Aaron Rodgers", "Josh Allen")
    print(comparison)
