import pandas as pd


def team_goal_stats(matches: pd.DataFrame) -> pd.DataFrame:
    """Per-team breakdown of goals and result distribution.

    Returns one row per team with: P, GF, GA, GF_per_match, GA_per_match,
    Total_goals_per_match, DrawRate, OneGoalRate, BlowoutRate (|diff| >= 2).
    """
    teams = sorted(set(matches["Home"]).union(matches["Away"]))
    rows = []
    for team in teams:
        home_games = matches[matches["Home"] == team]
        away_games = matches[matches["Away"] == team]
        n_total = len(home_games) + len(away_games)
        if n_total == 0:
            continue

        gf = int(home_games["HG"].sum() + away_games["AG"].sum())
        ga = int(home_games["AG"].sum() + away_games["HG"].sum())
        diffs = pd.concat([
            (home_games["HG"] - home_games["AG"]).abs(),
            (away_games["HG"] - away_games["AG"]).abs(),
        ])

        rows.append({
            "Team": team,
            "P": n_total,
            "GF": gf,
            "GA": ga,
            "GF_per_match": gf / n_total,
            "GA_per_match": ga / n_total,
            "Total_goals_per_match": (gf + ga) / n_total,
            "DrawRate": float((diffs == 0).mean()),
            "OneGoalRate": float((diffs == 1).mean()),
            "BlowoutRate": float((diffs >= 2).mean()),
        })

    return pd.DataFrame(rows).sort_values("GF_per_match", ascending=False).reset_index(drop=True)


def goal_diff_distribution(matches: pd.DataFrame, max_diff: int = 5) -> pd.Series:
    """Share of matches by absolute goal difference, capped at max_diff (bucket "max_diff+")."""
    diffs = (matches["HG"] - matches["AG"]).abs().clip(upper=max_diff)
    counts = diffs.value_counts().sort_index()
    counts = counts.reindex(range(max_diff + 1), fill_value=0)
    return counts / counts.sum()
