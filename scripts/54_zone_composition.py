"""Kompozycja ligi wg zagrożenia spadkiem — snapshoty co poniedziałek (Ekstraklasa 2025/26).

Skala pełna 0–18: dla każdej daty wszystkie 18 drużyn rozdzielone na cztery pasy
(stackplot, od dołu, gradient): czerwone = strefa spadkowa (16–18), pomarańczowe = strefa
paniki (≤3 pkt od 16. = jedna wygrana), żółte = strefa strachu (≤6 pkt od 16.), zielone =
bezpieczne. Pokazuje, jak mało było zieleni przez cały sezon.

Snapshot co poniedziałek — tabela uwzględnia wszystkie mecze rozegrane do niedzieli włącznie.
Rozłożone rundy i zaległe mecze wchodzą do tabeli w tygodniu, w którym zostały rozegrane.
Dane: POL.csv (sezon bieżący).
Output: figures/teams/fig123_zone_composition.png
"""
import _bootstrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from ekstraklasa.config import data_path, CURRENT_SEASON, FIG_TEAMS
from ekstraklasa.data.loaders import load_pol_season
from ekstraklasa.data.tables import table_snapshots_by_date
from ekstraklasa.plots.style import save_figure, clean_axes

RELEGATION_RANK = 16
PANIC_GAP = 3
FEAR_GAP = 6


def tuesday_dates(matches: pd.DataFrame) -> list[pd.Timestamp]:
    first = matches["Date"].min()
    last = matches["Date"].max()
    first_tuesday = first + pd.Timedelta(days=(1 - first.dayofweek) % 7)
    return pd.date_range(first_tuesday, last, freq="W-TUE").tolist()


def zone_composition(snapshots: pd.DataFrame) -> pd.DataFrame:
    border = snapshots[snapshots["Rank"] == RELEGATION_RANK].set_index("Date")["Pts"]
    enriched = snapshots.copy()
    enriched["distance"] = enriched["Pts"] - enriched["Date"].map(border)
    in_zone = enriched["Rank"] >= RELEGATION_RANK
    enriched["band"] = np.select(
        [in_zone,
         enriched["distance"] <= PANIC_GAP,
         enriched["distance"] <= FEAR_GAP],
        ["zone", "panic", "fear"], default="safe")
    counts = enriched.groupby(["Date", "band"]).size().unstack(fill_value=0)
    return counts.reindex(columns=["zone", "panic", "fear", "safe"], fill_value=0).reset_index()


matches = load_pol_season(data_path("POL.csv"), CURRENT_SEASON)
tuesdays = tuesday_dates(matches)
snapshots = table_snapshots_by_date(matches, dates=tuesdays)
composition = zone_composition(snapshots)

x = pd.to_datetime(composition["Date"])

fig, ax = plt.subplots(figsize=(12, 6))
ax.stackplot(x, composition["zone"], composition["panic"], composition["fear"], composition["safe"],
             colors=["#d32f2f", "#ff9800", "#ffd54f", "#4caf50"], alpha=0.95,
             labels=["Strefa spadkowa (16–18)", "Strefa paniki (≤3 pkt od 16.)",
                     "Strefa strachu (≤6 pkt od 16.)", "Bezpieczne"])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%y"))
ax.set_ylim(0, 18)
ax.set_yticks(range(0, 19, 3))
ax.set_xlim(x.min(), x.max())
ax.set_ylabel("Liczba drużyn (z 18)", fontsize=11)
ax.set_title("Ile drużyn było bezpiecznych w każdym momencie sezonu — Ekstraklasa 2025/26\n"
             "(im bliżej strefy spadkowej, tym cieplejszy kolor; zielone = bezpieczne)",
             fontsize=13, weight="bold")
ax.legend(loc="upper center", ncol=3, fontsize=9, framealpha=0.9)
clean_axes(ax)
fig.tight_layout()
save_figure(fig, "fig123_zone_composition.png", output_dir=FIG_TEAMS)
