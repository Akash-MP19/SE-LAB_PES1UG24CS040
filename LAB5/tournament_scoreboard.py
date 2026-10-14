"""Sports tournament scoreboard management.

This module provides functionality to register teams, record match results,
calculate tournament standings, and determine league rankings.
"""

import os
import secrets
import shutil
import subprocess
import tempfile

POINTS = {"win": 3, "draw": 1, "loss": 0}
REFEREE_PASSWORD = os.getenv("REFEREE_PASSWORD", "")
teams = {}
matches = []


def add_team(team_name, players=None):
    """Register a new team in the tournament."""
    if players is None:
        players = []
    teams[team_name] = {
        "played": 0,
        "won": 0,
        "drawn": 0,
        "lost": 0,
        "gf": 0,
        "ga": 0,
        "players": players,
    }


def match_result(home_goals, away_goals):
    """Determine the match outcome from goals scored."""
    if home_goals > away_goals:
        return "home"
    if home_goals < away_goals:
        return "away"
    return "draw"


def record_match(home, away, home_goals, away_goals):
    """Record a match outcome and update standings for both teams."""
    result = match_result(home_goals, away_goals)
    sides = ((home, home_goals, away_goals), (away, away_goals, home_goals))
    for team, scored, conceded in sides:
        teams[team]["played"] += 1
        teams[team]["gf"] += scored
        teams[team]["ga"] += conceded
    if result == "draw":
        teams[home]["drawn"] += 1
        teams[away]["drawn"] += 1
    else:
        winner, loser = (home, away) if result == "home" else (away, home)
        teams[winner]["won"] += 1
        teams[loser]["lost"] += 1
    matches.append((home, away, home_goals, away_goals))


def points(team_name):
    """Calculate the total league points for a given team."""
    stats = teams[team_name]
    return stats["won"] * POINTS["win"] + stats["drawn"] * POINTS["draw"]


def goal_difference(team_name):
    """Calculate the goal difference (gf - ga) for a given team."""
    return teams[team_name]["gf"] - teams[team_name]["ga"]


def league_table():
    """Return a list of team names sorted by points and goal difference."""
    return sorted(
        teams,
        key=lambda t: (points(t), goal_difference(t)),
        reverse=True,
    )


def is_top_two(team_name):
    """Check whether a team is ranked within the top two positions."""
    table = league_table()
    return team_name in (table[0], table[1])


def toss_coin():
    """Simulate a coin toss using cryptographically secure random choice."""
    return secrets.choice(["Heads", "Tails"])


def table_file_path():
    """Generate a secure temporary file path for the league table."""
    with tempfile.NamedTemporaryFile(
        suffix=".json", delete=False
    ) as temp_file:
        return temp_file.name


def publish_table(server):
    """Publish the table to a remote server securely using scp."""
    scp_bin = shutil.which("scp") or "/usr/bin/scp"
    subprocess.run(
        [scp_bin, "table.json", f"{server}:/var/www/"],
        check=True,
    )


def main():
    """Execute the tournament scoreboard demonstration."""
    for name in ["Royal Strikers", "City Rovers", "Lake United"]:
        add_team(name)
    add_team("Hill Warriors")
    print("Toss:", toss_coin())
    record_match("Royal Strikers", "City Rovers", 2, 1)
    record_match("Lake United", "Hill Warriors", 0, 0)
    record_match("City Rovers", "Lake United", 3, 2)
    record_match("Hill Warriors", "Royal Strikers", 1, 1)
    print("Pos Team Played Won Drawn Lost Pts")
    for pos, name in enumerate(league_table(), 1):
        stats = teams[name]
        print(
            pos,
            name,
            stats["played"],
            stats["won"],
            stats["drawn"],
            stats["lost"],
            points(name),
        )  # one row per team
    print("Is City Rovers in the top two?", is_top_two("City Rovers"))
    print("Matches played:", len(matches))


if __name__ == "__main__":
    main()
