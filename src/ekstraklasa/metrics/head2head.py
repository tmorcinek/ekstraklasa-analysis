"""Macierze bezpośrednich pojedynków (head-to-head) i odczyty strukturalne.

Warstwa danych — zwraca DataFrame/dict, bez matplotlib.
Macierze indeksowane porządkiem końcowej tabeli (1. miejsce pierwsze).
"""
import numpy as np
import pandas as pd

from ekstraklasa.data.tables import build_table


def _ordered_teams(matches: pd.DataFrame) -> list[str]:
    return build_table(matches)["Team"].tolist()


def points_matrix(matches: pd.DataFrame, order: list[str] | None = None) -> pd.DataFrame:
    """Komórka (i, j) = punkty, jakie drużyna i zdobyła z drużyną j (suma obu meczów, 0–6)."""
    teams = order or _ordered_teams(matches)
    idx = {t: k for k, t in enumerate(teams)}
    M = np.zeros((len(teams), len(teams)))
    for _, m in matches.iterrows():
        h, a, hg, ag = m["Home"], m["Away"], m["HG"], m["AG"]
        if h not in idx or a not in idx:
            continue
        if hg > ag:
            M[idx[h], idx[a]] += 3
        elif hg < ag:
            M[idx[a], idx[h]] += 3
        else:
            M[idx[h], idx[a]] += 1
            M[idx[a], idx[h]] += 1
    np.fill_diagonal(M, np.nan)
    return pd.DataFrame(M, index=teams, columns=teams)


def goals_matrix(matches: pd.DataFrame, order: list[str] | None = None) -> pd.DataFrame:
    """Komórka (i, j) = gole strzelone przez i przeciw j (suma obu meczów)."""
    teams = order or _ordered_teams(matches)
    idx = {t: k for k, t in enumerate(teams)}
    M = np.zeros((len(teams), len(teams)))
    for _, m in matches.iterrows():
        h, a, hg, ag = m["Home"], m["Away"], m["HG"], m["AG"]
        if h not in idx or a not in idx:
            continue
        M[idx[h], idx[a]] += hg
        M[idx[a], idx[h]] += ag
    np.fill_diagonal(M, np.nan)
    return pd.DataFrame(M, index=teams, columns=teams)


def h2h_readings(points_df: pd.DataFrame) -> dict:
    """Odczyty strukturalne z macierzy punktów (porządek = końcowa tabela).

    Zwraca słownik metryk: bilans hierarchii, upsety, intranzytywność,
    rozkład punktów lidera, koncentracja przewagi czołówki.
    """
    teams = list(points_df.index)
    n = len(teams)
    M = points_df.values  # M[i,j] = pkt i z j; wyższa pozycja = niższy indeks

    # --- A4a: bilans hierarchii po parach ---
    higher_pts = lower_pts = 0.0
    higher_won = ties = lower_won = 0
    for i in range(n):
        for j in range(i + 1, n):  # i wyżej w tabeli niż j
            hi, lo = M[i, j], M[j, i]
            higher_pts += hi
            lower_pts += lo
            if hi > lo:
                higher_won += 1
            elif hi < lo:
                lower_won += 1
            else:
                ties += 1
    n_pairs = n * (n - 1) // 2

    # --- A4b: upsety (niżej sklasyfikowany ugrał >= / > pkt) ---
    upsets_ge = lower_won + ties
    upsets_gt = lower_won

    # --- A4d: intranzytywność (cykle 3-elementowe w relacji dominacji H2H) ---
    D = np.zeros((n, n), dtype=int)  # D[i,j]=1 gdy i ugrał z j więcej pkt
    for i in range(n):
        for j in range(n):
            if i != j and M[i, j] > M[j, i]:
                D[i, j] = 1
    # liczymy triady, w których wszystkie 3 pary są rozstrzygnięte (bez remisu H2H);
    # cykl = każda z trzech drużyn ma dokładnie 1 zwycięstwo i 1 porażkę w triadzie
    decisive = cyc = 0
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                e = [D[a, b] or D[b, a], D[b, c] or D[c, b], D[a, c] or D[c, a]]
                if all(e):
                    decisive += 1
                    # cykl jeśli każdy ma dokładnie jedno zwycięstwo i jedną porażkę
                    wins = {a: 0, b: 0, c: 0}
                    for x, y in [(a, b), (b, c), (a, c)]:
                        if D[x, y]:
                            wins[x] += 1
                        else:
                            wins[y] += 1
                    if set(wins.values()) == {1}:
                        cyc += 1

    # --- A4c/e: rozkład punktów lidera i koncentracja przewagi czołówki ---
    leader_row = M[0]
    leader_vs_top = np.nansum(leader_row[1:6])     # vs miejsca 2–6
    leader_vs_mid = np.nansum(leader_row[6:12])    # vs 7–12
    leader_vs_bot = np.nansum(leader_row[12:])     # vs 13–18

    half = n // 2
    top_vs_bottom = np.nansum(M[:half, half:])     # pkt czołówki przeciw dołowi
    bottom_vs_top = np.nansum(M[half:, :half])     # pkt dołu przeciw czołówce

    return {
        "n_teams": n,
        "n_pairs": n_pairs,
        "higher_pts_total": higher_pts,
        "lower_pts_total": lower_pts,
        "pairs_higher_won": higher_won,
        "pairs_tied": ties,
        "pairs_lower_won": lower_won,
        "upsets_ge": upsets_ge,
        "upset_rate_ge": upsets_ge / n_pairs,
        "upsets_gt": upsets_gt,
        "triples_decisive": decisive,
        "triples_cyclic": cyc,
        "cyclic_rate": (cyc / decisive) if decisive else float("nan"),
        "leader_vs_top(2-6)": leader_vs_top,
        "leader_vs_mid(7-12)": leader_vs_mid,
        "leader_vs_bot(13-18)": leader_vs_bot,
        "top_half_vs_bottom_half_pts": top_vs_bottom,
        "bottom_half_vs_top_half_pts": bottom_vs_top,
    }
