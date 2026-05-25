import pandas as pd

from ekstraklasa.data.tables import build_table


def position_changes(prev_matches: pd.DataFrame, curr_matches: pd.DataFrame,
                     n_relegated: int = 3) -> pd.DataFrame:
    """Per-team position change between two seasons.

    Teams promoted into the current season (not present in previous) are paired
    with the bottom n_relegated positions of the previous season — best promoted
    team (lowest current rank) gets the highest of the bottom positions, the worst
    promoted team gets the lowest. This makes Diff well-defined for every team.

    Diff = PrevRank - CurrRank (positive = improved).
    """
    prev_table = build_table(prev_matches)
    curr_table = build_table(curr_matches)

    prev_rank_by_team = dict(zip(prev_table["Team"], prev_table.index))
    curr_rank_by_team = dict(zip(curr_table["Team"], curr_table.index))

    promoted = set(curr_rank_by_team) - set(prev_rank_by_team)
    bottom_prev_ranks = sorted(prev_rank_by_team.values())[-n_relegated:]
    promoted_sorted = sorted(promoted, key=lambda team: curr_rank_by_team[team])
    promoted_assigned_prev = dict(zip(promoted_sorted, bottom_prev_ranks))

    rows = []
    for team, curr_rank in curr_rank_by_team.items():
        if team in promoted:
            prev_rank = promoted_assigned_prev[team]
            kind = "promoted"
        else:
            prev_rank = prev_rank_by_team[team]
            kind = "stayed"
        diff = prev_rank - curr_rank
        rows.append({
            "Team": team,
            "PrevRank": prev_rank,
            "CurrRank": curr_rank,
            "Diff": diff,
            "AbsDiff": abs(diff),
            "Kind": kind,
        })

    return pd.DataFrame(rows).sort_values("CurrRank").reset_index(drop=True)
