from app.queries import compare_players, get_player_average, get_team_average
import re

TEAM_MAP = {
    "arizona cardinals": "ARI",
    "cardinals": "ARI",

    "atlanta falcons": "ATL",
    "falcons": "ATL",

    "baltimore ravens": "BAL",
    "ravens": "BAL",

    "buffalo bills": "BUF",
    "bills": "BUF",

    "carolina panthers": "CAR",
    "panthers": "CAR",

    "chicago bears": "CHI",
    "bears": "CHI",

    "cincinnati bengals": "CIN",
    "bengals": "CIN",

    "cleveland browns": "CLE",
    "browns": "CLE",

    "dallas cowboys": "DAL",
    "cowboys": "DAL",

    "denver broncos": "DEN",
    "broncos": "DEN",

    "detroit lions": "DET",
    "lions": "DET",

    "green bay packers": "GB",
    "packers": "GB",

    "houston texans": "HOU",
    "texans": "HOU",

    "indianapolis colts": "IND",
    "colts": "IND",

    "jacksonville jaguars": "JAX",
    "jaguars": "JAX",

    "kansas city chiefs": "KC",
    "chiefs": "KC",

    "las vegas raiders": "LV",
    "raiders": "LV",

    "los angeles chargers": "LAC",
    "chargers": "LAC",

    "los angeles rams": "LA",
    "rams": "LA",

    "miami dolphins": "MIA",
    "dolphins": "MIA",

    "minnesota vikings": "MIN",
    "vikings": "MIN",

    "new england patriots": "NE",
    "patriots": "NE",

    "new orleans saints": "NO",
    "saints": "NO",

    "new york giants": "NYG",
    "giants": "NYG",

    "new york jets": "NYJ",
    "jets": "NYJ",

    "philadelphia eagles": "PHI",
    "eagles": "PHI",

    "pittsburgh steelers": "PIT",
    "steelers": "PIT",

    "san francisco 49ers": "SF",
    "49ers": "SF",

    "seattle seahawks": "SEA",
    "seahawks": "SEA",

    "tampa bay buccaneers": "TB",
    "buccaneers": "TB",
    "bucs": "TB",

    "tennessee titans": "TEN",
    "titans": "TEN",

    "washington commanders": "WAS",
    "commanders": "WAS"
}

def extract_team(prompt):
    """Extract a team name from the prompt."""
    text = prompt.lower()

    for team_name in TEAM_MAP:
        if team_name in text:
            return TEAM_MAP[team_name]

    return None

def extract_players(prompt):
    """Extract two player names from a comparison-style prompt."""
    cleaned = prompt.strip().replace("?", "")

    if " or " in cleaned:
        parts = cleaned.split(" or ", maxsplit=1)
    elif " vs " in cleaned:
        parts = cleaned.split(" vs ", maxsplit=1)
    elif " versus " in cleaned:
        parts = cleaned.split(" versus ", maxsplit=1)
    else:
        return None, None

    left = parts[0].strip()
    right = parts[1].strip()

    prefixes = [
            "Should I start ",
            "Compare ",
            "Who is better ",
            "Start ",
            ]

    for prefix in prefixes:
        if left.startswith(prefix):
            left = left.replace(prefix, "", 1).strip()

    return left, right

def extract_single_player(prompt):
    """Extract a player name for performance queries."""
    cleaned = prompt.strip().replace("?", "")

    prefixes = [
            "How has ",
            "How is ",
            "Show recent performance for ",
            "Show performance for ",
            ]

    for prefix in prefixes:
        if cleaned.startswith(prefix):
            name = cleaned.replace(prefix, "", 1)
            name = name.replace(" performed recently", "")
            name = name.replace(" playing", "")
            return name.strip()

    return None

def extract_two_teams(prompt):
    """Extract up to two team codes from the prompt."""
    text = prompt.lower()
    found_teams = []

    for team_name, team_code in TEAM_MAP.items():
        if team_name in text and team_code not in found_teams:
            found_teams.append(team_code)

    if len(found_teams) >= 2:
        return found_teams[0], found_teams[1]

    return None, None

def extract_spread(prompt):
    """Extract a betting spread like +4.5 or -3.0 from the prompt."""
    match = re.search(r"([+-]\d+(\.\d+)?)", prompt)

    if match:
        return float(match.group(1))

    return None

def run_agent(prompt):
    """Process a user prompt and return a response."""

    # 1. Single-player query
    player = extract_single_player(prompt)
    if player is not None:
        stats = get_player_average(player)

        if stats is None:
            return f"Sorry, I could not find data for {player}."

        return f"""
Recent Performance: {stats['name']}

Last {stats['games_used']} Games

Average Fantasy Points: {stats['avg_fantasy_points']:.2f}
Average Rushing Yards: {stats['avg_rushing_yards']:.2f}
Average Receiving Yards: {stats['avg_receiving_yards']:.2f}
Average Touchdowns: {(stats['avg_rushing_tds'] + stats['avg_receiving_tds']):.2f}
"""
    # 2. Betting-style team evaluation
    team_a, team_b = extract_two_teams(prompt)
    spread = extract_spread(prompt)

    if team_a and team_b and spread is not None:
        stats_a = get_team_average(team_a)
        stats_b = get_team_average(team_b)

        if stats_a is None or stats_b is None:
            return "Sorry, I could not find enough data to evaluate that matchup."

        lean = None
        reason = ""

        if stats_a["avg_fantasy_points"] >= stats_b["avg_fantasy_points"]:
            lean = f"{team_a} {spread:+}"
            reason = f"{team_a} has matched or exceeded {team_b} in recent fantasy-based team production."
        else:
            lean = "Pass"
            reason = f"{team_b} has looked stronger recently, so the spread may not offer enough value."

        return f"""
Bet Evaluation: {team_a} vs {team_b} ({spread:+})

Recent Team Form

{team_a}
Average Fantasy Output: {stats_a['avg_fantasy_points']:.2f}
Average Total TDs: {(stats_a['avg_rushing_tds'] + stats_a['avg_receiving_tds']):.2f}

{team_b}
Average Fantasy Output: {stats_b['avg_fantasy_points']:.2f}
Average Total TDs: {(stats_b['avg_rushing_tds'] + stats_b['avg_receiving_tds']):.2f}

Lean: {lean}

Reason: {reason}

Risk: This recommendation is based on recent historical production only and does not account for injuries, live odds movement, or defensive matchup adjustments.
"""
# 3. Team performance query
    team = extract_team(prompt)

    if team:
        stats = get_team_average(team)

        if stats is None:
            return f"Sorry, I could not find recent data for {team}."

        return f"""
Recent Team Performance: {team}

Last {stats['games_used']} Games

Average Rushing Yards: {stats['avg_rushing_yards']:.2f}
Average Receiving Yards: {stats['avg_receiving_yards']:.2f}
Average Touchdowns: {(stats['avg_rushing_tds'] + stats['avg_receiving_tds']):.2f}
Average Fantasy Output: {stats['avg_fantasy_points']:.2f}
    """
    # 4. Comparison query
    player_a, player_b = extract_players(prompt)
    if player_a is not None and player_b is not None:
        comparison = compare_players(player_a, player_b)

        if isinstance(comparison, str):
            return comparison

        player_a_stats = comparison["player_a"]
        player_b_stats = comparison["player_b"]
        recommendation = comparison["recommendation"]
        reason = comparison["reason"]

        return f"""
Comparison: {player_a_stats['name']} vs {player_b_stats['name']}

Recent Performance (Last {player_a_stats['games_used']} Games)

{player_a_stats['name']}
Average Fantasy Points: {player_a_stats['avg_fantasy_points']:.2f}

{player_b_stats['name']}
Average Fantasy Points: {player_b_stats['avg_fantasy_points']:.2f}

Recommendation: {recommendation}

Reason: {reason}
"""

    # 5. Fallback
    return "Sorry, I couldn't understand the request. Try comparing two players or asking about recent performance."

if __name__ == "__main__":
    prompt = "Should I go with Arizona Cardinals over the San Francisco 49ers at +4.5?"
    print(run_agent(prompt))


