from app.queries import compare_players

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

def run_agent(prompt):
    """Process a user prompt and return a response."""
    player_a, player_b = extract_players(prompt)

    if not player_a or not player_b:
        return "Sorry, I could not identify two players to compare."
    
    comparison = compare_players(player_a, player_b)

    if isinstance(comparison, str):
        return comparison

    player_a_stats = comparison["player_a"]
    player_b_stats = comparison["player_b"]
    recommendation = comparison["recommendation"]
    reason = comparison["reason"]

    response = f"""
    Comparison: {player_a_stats['name']} vs {player_b_stats['name']}

    Recent Performance (Last {player_a_stats['games_used']} Games)

    {player_a_stats['name']}
    Average Fantasy Points: {player_a_stats['avg_fantasy_points']:.2f}

    {player_b_stats['name']}
    Average Fantasy Points: {player_b_stats['avg_fantasy_points']:.2f}

    Recommendation: {recommendation}

    Reason: {reason}
    """

    return response


if __name__ == "__main__":
    prompt = "Should I start Aaron Rodgers or Josh Allen?"
    print(run_agent(prompt))


