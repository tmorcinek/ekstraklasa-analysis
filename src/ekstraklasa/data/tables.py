from typing import Callable

import numpy as np
import pandas as pd

# Tiebreaker = funkcja sortująca grupę drużyn o tej samej liczbie punktów.
# Sygnatura: (group: DataFrame z kolumnami Team, GF, GA, GD, ...; matches: DataFrame) -> list[str]
# Zwraca nazwy drużyn w kolejności od najwyższego miejsca do najniższego.
Tiebreaker = Callable[[pd.DataFrame, pd.DataFrame], list]


def simple_tiebreaker(group: pd.DataFrame, matches: pd.DataFrame) -> list:
    """Top 5 / UEFA-domyślny: różnica bramek, potem bramki strzelone (oba w skali całego sezonu)."""
    return group.sort_values(["GD", "GF"], ascending=[False, False])["Team"].tolist()


def head_to_head_tiebreaker(group: pd.DataFrame, matches: pd.DataFrame) -> list:
    """Regulamin Ekstraklasy: przy równości punktów najpierw mini-tabela bezpośrednich meczów
    (punkty H2H → różnica bramek H2H → bramki strzelone H2H), a dopiero potem różnica bramek
    i bramki strzelone z całego sezonu."""
    teams = set(group["Team"])
    if len(teams) == 1:
        return list(teams)

    mini = {t: {"pts": 0, "gf": 0, "ga": 0} for t in teams}
    for _, m in matches.iterrows():
        h, a, hg, ag = m["Home"], m["Away"], m["HG"], m["AG"]
        if h not in teams or a not in teams:
            continue  # tylko mecze WEWNĄTRZ remisującej grupy
        mini[h]["gf"] += hg; mini[h]["ga"] += ag
        mini[a]["gf"] += ag; mini[a]["ga"] += hg
        if hg > ag:
            mini[h]["pts"] += 3
        elif hg < ag:
            mini[a]["pts"] += 3
        else:
            mini[h]["pts"] += 1; mini[a]["pts"] += 1

    overall = group.set_index("Team")
    def key(t):
        return (
            mini[t]["pts"],
            mini[t]["gf"] - mini[t]["ga"],   # różnica bramek H2H
            mini[t]["gf"],                    # bramki strzelone H2H
            overall.loc[t, "GD"],             # różnica bramek (sezon)
            overall.loc[t, "GF"],             # bramki strzelone (sezon)
        )
    return sorted(teams, key=key, reverse=True)


def build_table(matches: pd.DataFrame, tiebreaker: Tiebreaker = simple_tiebreaker) -> pd.DataFrame:
    """Tabela 3-1-0. Sortuje malejąco po punktach; remisy punktowe rozstrzyga wstrzyknięty
    `tiebreaker` (domyślnie GD, GF). Indeks miejsca zaczyna się od 1."""
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

    # sortowanie: malejąco po punktach, w obrębie każdej grupy punktowej — wg tiebreakera
    ordered_teams = []
    for _, group in table.sort_values("Pts", ascending=False).groupby("Pts", sort=False):
        ordered_teams.extend(tiebreaker(group, matches))

    table = table.set_index("Team").loc[ordered_teams].reset_index()
    table.index = table.index + 1
    return table


# rejestr strategii — wstrzykiwany per liga (tag w config.LEAGUES["...']["tiebreak"])
TIEBREAKERS: dict[str, Tiebreaker] = {
    "simple": simple_tiebreaker,
    "h2h": head_to_head_tiebreaker,
}


def build_league_table(name: str, matches: pd.DataFrame) -> pd.DataFrame:
    """Buduje tabelę z mechanizmem rozstrzygania remisów właściwym dla danej ligi (wg config)."""
    from ekstraklasa.config import LEAGUES
    tag = LEAGUES.get(name, {}).get("tiebreak", "simple")
    return build_table(matches, tiebreaker=TIEBREAKERS[tag])


def balanced_snapshot_dates(matches: pd.DataFrame, max_imbalance: int = 1) -> pd.DataFrame:
    """Daty, po których wszystkie drużyny rozegrały tyle samo meczów (±max_imbalance).

    Jedna data na poziom k — moment najbardziej wyrównanej tabeli na tym poziomie. Eliminuje
    zakrzywienia wnoszone przez zaległe mecze (≈34 czyste daty zamiast ~125). Zwraca DataFrame
    [k, Date]."""
    ordered = matches.sort_values("Date")
    teams = set(ordered["Home"]).union(ordered["Away"])
    game_count = {team: 0 for team in teams}
    candidates: dict[int, pd.Timestamp] = {}
    for _, row in ordered.iterrows():
        game_count[row["Home"]] += 1
        game_count[row["Away"]] += 1
        counts = game_count.values()
        if max(counts) - min(counts) <= max_imbalance:
            candidates[min(counts)] = row["Date"]
    return pd.DataFrame([{"k": k, "Date": date} for k, date in sorted(candidates.items())])


def table_snapshots_by_date(matches: pd.DataFrame, league: str = "Ekstraklasa",
                            from_date: str | None = None, dates=None,
                            require_full_roster: bool = True) -> pd.DataFrame:
    """Pełna tabela po datach meczowych (ze wszystkich meczów do danej daty włącznie).

    Respektuje przełożone mecze — mecz wchodzi do tabeli w dniu rozegrania, nie w nominalnej
    kolejce. Domyślnie próbkuje każdą unikalną datę meczową; podaj `dates` (np. z
    `balanced_snapshot_dates`), by ograniczyć się do wybranych dat. Zwraca długi DataFrame:
    Date, Rank, Team, Pts, P, W, D, L, GF, GA, GD, PPG. Pomija daty, zanim wszystkie drużyny
    rozegrały choć jeden mecz."""
    ordered = matches.sort_values("Date")
    roster = set(ordered["Home"]).union(ordered["Away"])
    if dates is not None:
        snapshot_dates = sorted(pd.Timestamp(date) for date in dates)
    else:
        snapshot_dates = sorted(ordered["Date"].unique())
        if from_date is not None:
            cutoff = pd.Timestamp(from_date)
            snapshot_dates = [date for date in snapshot_dates if date >= cutoff]

    frames = []
    for snapshot_date in snapshot_dates:
        played = ordered[ordered["Date"] <= snapshot_date]
        if require_full_roster and set(played["Home"]).union(played["Away"]) != roster:
            continue
        table = build_league_table(league, played).reset_index().rename(columns={"index": "Rank"})
        table["Date"] = snapshot_date
        frames.append(table)
    return pd.concat(frames, ignore_index=True)


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
