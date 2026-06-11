"""Pochodne wskaźniki stylu i agregacja sezonowa per drużyna.

Warstwa danych — przyjmuje/zwraca DataFrame, bez matplotlib.
Wejście: dane meczowe (jeden wiersz = drużyna w meczu) z kolumnami surowymi
i `PPDA` (liczone w 33_style_exploration.load_stats, zapisane w style_per_match.csv).
"""
import numpy as np
import pandas as pd

# 6 wskaźników stylu pokazywanych w fig60 i siatkach output/figures/style/esa/.
# Klucz = kolumna (po add_style_metrics), wartość = etykieta na wykresie.
ESA_STYLE_METRICS = {
    "Ball possession": "Posiadanie (%)",
    "Passes": "Liczba podań",
    "long_pass_pct": "Długie podania (% podań)",
    "PPDA": "PPDA (niżej = wyższy pressing)",
    "final_third_pass_pct": "Podania w ostatniej tercji (% podań)",
    "Clearances": "Wybicia",
}

# Podzbiór cech "kształtu gry" do analizy rozrzutu/outlierów — bez PPDA i wybić
# (pressing hałaśliwy, wybicia to sygnał defensywny dołu, nie tożsamości stylu).
STYLE_SHAPE_METRICS = ["Ball possession", "Passes", "long_pass_pct", "final_third_pass_pct"]


def add_ppda(matches: pd.DataFrame) -> pd.DataFrame:
    """Dokłada PPDA = podania rywala / (nasze odbiory + przechwyty + faule).

    Wymaga kolumn: match_id, is_home, Passes, Tackles, Interceptions, Fouls.
    Zakłada dwa wiersze (gospodarz + gość) na match_id.
    """
    df = matches.copy()
    home_passes = df[df["is_home"]].set_index("match_id")["Passes"]
    away_passes = df[~df["is_home"]].set_index("match_id")["Passes"]
    df = df.set_index("match_id")
    df.loc[df["is_home"], "opp_passes"] = away_passes
    df.loc[~df["is_home"], "opp_passes"] = home_passes
    df = df.reset_index()
    press_denom = df["Tackles"].fillna(0) + df["Interceptions"].fillna(0) + df["Fouls"].fillna(0)
    df["PPDA"] = df["opp_passes"] / (press_denom + 1e-6)
    return df


def add_style_metrics(matches: pd.DataFrame) -> pd.DataFrame:
    """Dokłada pochodne wskaźniki stylu (udziały %) do danych meczowych.

    Liczniki długich podań / podań w tercji to próby (kolumny `- Total`).
    """
    df = matches.copy()
    passes = df["Passes"].replace(0, np.nan)
    df["long_pass_pct"] = 100 * df["Long balls - Total"] / passes
    df["final_third_pass_pct"] = 100 * df["Final third phase - Total"] / passes
    df["pass_accuracy"] = 100 * df["Accurate passes"] / passes
    df["shot_accuracy"] = 100 * df["Shots on target"] / df["Total shots"].replace(0, np.nan)
    if "PPDA" in df.columns:
        df["pressing_intensity"] = -df["PPDA"]
    return df


def team_season_means(matches: pd.DataFrame, metrics: list[str], by: str = "team_short") -> pd.DataFrame:
    """Średnie sezonowe wybranych wskaźników per drużyna (indeks = kolumna `by`)."""
    return matches.groupby(by)[metrics].mean()
