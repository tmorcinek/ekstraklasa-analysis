"""Kto strzela pierwszy — czy decydujący pierwszy gol respektuje klasę.

Łączy prawdziwego „pierwszego strzelca" z danych zdarzeniowych (export/) z kursami
bukmacherskimi (data/), wyznacza faworyta meczu (niższy kurs) i liczy, jak często to
faworyt otwiera wynik — dla trzech lig.

Dane wejściowe:
  data/{slug}_progress.csv         — pierwszy strzelec, wynik
  data/{POL,E0,P1}.csv             — kursy (Ekstraklasa: zamykające AvgC*, EPL/Portugalia: Avg*)
Output:
  csv/leagues/first_goal_favourite.csv        — odsetek „faworyt strzela pierwszy" per liga
  figures/leagues/fig118_favourite_scores_first_leagues.png
"""
import _bootstrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ekstraklasa.config import data_path, FIG_LEAGUES, CSV_LEAGUES, COLORS, TEAM_MAP
from ekstraklasa.plots.style import save_figure, clean_axes
PORTUGAL_COLOR = "#2e7d32"

EPL_TEAM_MAP = {
    "Arsenal": "Arsenal", "Aston Villa": "Aston Villa", "Bournemouth": "Bournemouth",
    "Brentford": "Brentford", "Brighton & Hove Albion": "Brighton", "Burnley": "Burnley",
    "Chelsea": "Chelsea", "Crystal Palace": "Crystal Palace", "Everton": "Everton",
    "Fulham": "Fulham", "Leeds United": "Leeds", "Liverpool FC": "Liverpool",
    "Manchester City": "Man City", "Manchester United": "Man United",
    "Newcastle United": "Newcastle", "Nottingham Forest": "Nott'm Forest",
    "Sunderland": "Sunderland", "Tottenham Hotspur": "Tottenham",
    "West Ham United": "West Ham", "Wolverhampton": "Wolves",
}
PORTUGAL_TEAM_MAP = {
    "AVS - Futebol SAD": "AVS", "Benfica": "Benfica", "CD Nacional": "Nacional",
    "CF Estrela Amadora": "Estrela", "Casa Pia": "Casa Pia", "Estoril Praia": "Estoril",
    "FC Alverca": "Alverca", "FC Arouca": "Arouca", "FC Porto": "Porto",
    "Famalicão": "Famalicao", "Gil Vicente": "Gil Vicente", "Moreirense": "Moreirense",
    "Rio Ave": "Rio Ave", "Santa Clara": "Santa Clara", "Sporting Braga": "Sp Braga",
    "Sporting CP": "Sp Lisbon", "Tondela": "Tondela", "Vitória SC": "Guimaraes",
}

LEAGUES = {
    "Ekstraklasa": dict(slug="ekstraklasa", odds_file="POL.csv", team_map=TEAM_MAP,
                        odds_cols=("AvgCH", "AvgCD", "AvgCA"), season="2025/2026",
                        home_col="Home", away_col="Away", color=COLORS["Ekstraklasa"]),
    "Premier League": dict(slug="premier-league", odds_file="E0.csv", team_map=EPL_TEAM_MAP,
                           odds_cols=("AvgH", "AvgD", "AvgA"), season=None,
                           home_col="HomeTeam", away_col="AwayTeam", color=COLORS["EPL"]),
    "Liga Portugal": dict(slug="liga-portugal-betclic", odds_file="P1.csv", team_map=PORTUGAL_TEAM_MAP,
                          odds_cols=("AvgH", "AvgD", "AvgA"), season=None,
                          home_col="HomeTeam", away_col="AwayTeam", color=PORTUGAL_COLOR),
}


def favourite_first_df(config: dict) -> pd.DataFrame:
    progress = pd.read_csv(data_path(f"{config['slug']}_progress.csv"))
    progress = progress[progress["first_scorer"].isin(["home", "away"])].copy()
    progress["date"] = pd.to_datetime(progress["match_date"]).dt.date
    progress["home_fd"] = progress["home_name"].map(config["team_map"])
    progress["away_fd"] = progress["away_name"].map(config["team_map"])

    home, draw, away = config["odds_cols"]
    odds = pd.read_csv(data_path(config["odds_file"]))
    if config["season"]:
        odds = odds[odds["Season"] == config["season"]]
    odds = odds.rename(columns={config["home_col"]: "home_fd", config["away_col"]: "away_fd"})
    odds = odds[["Date", "home_fd", "away_fd", home, draw, away]].rename(
        columns={home: "odds_home", draw: "odds_draw", away: "odds_away"}).copy()
    odds["date"] = pd.to_datetime(odds["Date"], dayfirst=True).dt.date

    merged = progress.merge(odds, on=["date", "home_fd", "away_fd"], how="left").dropna(
        subset=["odds_home", "odds_draw", "odds_away"])
    favourite_side = np.where(merged["odds_home"] < merged["odds_away"], "home", "away")
    return pd.DataFrame({
        "favourite_first": merged["first_scorer"].to_numpy() == favourite_side,
    })


frames = {league: favourite_first_df(config) for league, config in LEAGUES.items()}

overall = pd.DataFrame({
    league: {"matches": len(frame), "favourite_first_pct": round(100 * frame["favourite_first"].mean(), 1)}
    for league, frame in frames.items()}).T.rename_axis("league").reset_index()

CSV_LEAGUES.mkdir(parents=True, exist_ok=True)
overall.to_csv(CSV_LEAGUES / "first_goal_favourite.csv", index=False)
print(overall.to_string(index=False))

# ── fig118: odsetek „faworyt strzela pierwszy" — trzy ligi ────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
colors = [LEAGUES[league]["color"] for league in overall["league"]]
bars = ax.bar(overall["league"], overall["favourite_first_pct"], color=colors, edgecolor="black", linewidth=0.5)
ax.axhline(50, color="#555", linestyle="--", linewidth=1.2, label="rzut monetą (50%)")
for bar, value in zip(bars, overall["favourite_first_pct"]):
    ax.text(bar.get_x() + bar.get_width() / 2, value + 0.8, f"{value:.1f}%", ha="center", fontsize=11, weight="bold")
ax.set_ylabel("Mecze, w których faworyt strzela pierwszy (%)", fontsize=11)
ax.set_ylim(0, 80)
ax.set_title("Czy faworyt zdobywa decydującego pierwszego gola? (2025/26)", fontsize=12, weight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
clean_axes(ax)
fig.tight_layout()
save_figure(fig, "fig118_favourite_scores_first_leagues.png", output_dir=FIG_LEAGUES)
