import numpy as np
import pandas as pd


def build_table(matches: pd.DataFrame) -> pd.DataFrame:
    """Standard 3-1-0 league table sorted by Pts, GD, GF (rank index starting at 1)."""
    teams = sorted(set(matches["Home"]).union(set(matches["Away"])))
    record = {team: {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0} for team in teams}

    for _, match in matches.iterrows():
        home, away, home_goals, away_goals = match["Home"], match["Away"], match["HG"], match["AG"]
        record[home]["P"] += 1
        record[away]["P"] += 1
        record[home]["GF"] += home_goals
        record[home]["GA"] += away_goals
        record[away]["GF"] += away_goals
        record[away]["GA"] += home_goals
        if home_goals > away_goals:
            record[home]["W"] += 1
            record[away]["L"] += 1
            record[home]["Pts"] += 3
        elif home_goals < away_goals:
            record[away]["W"] += 1
            record[home]["L"] += 1
            record[away]["Pts"] += 3
        else:
            record[home]["D"] += 1
            record[away]["D"] += 1
            record[home]["Pts"] += 1
            record[away]["Pts"] += 1

    table = pd.DataFrame.from_dict(record, orient="index").reset_index().rename(columns={"index": "Team"})
    table["GD"] = table["GF"] - table["GA"]
    table["PPG"] = table["Pts"] / table["P"]
    table = table.sort_values(["Pts", "GD", "GF"], ascending=[False, False, False]).reset_index(drop=True)
    table.index = table.index + 1
    return table


def points_by_team(matches: pd.DataFrame, teams: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Return (points, games_played) arrays aligned to the given team list order."""
    points = {team: 0 for team in teams}
    games = {team: 0 for team in teams}
    for _, match in matches.iterrows():
        home, away, home_goals, away_goals = match["Home"], match["Away"], match["HG"], match["AG"]
        games[home] += 1
        games[away] += 1
        if home_goals > away_goals:
            points[home] += 3
        elif home_goals < away_goals:
            points[away] += 3
        else:
            points[home] += 1
            points[away] += 1
    return (np.array([points[t] for t in teams]),
            np.array([games[t] for t in teams]))
