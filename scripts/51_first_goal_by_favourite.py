"""Kto strzela pierwszy — czy decydujący pierwszy gol respektuje klasę.

Łączy prawdziwego „pierwszego strzelca" z danych zdarzeniowych (export/) z kursami
bukmacherskimi (data/), wyznacza faworyta meczu (niższy kurs) i liczy, jak często to
faworyt otwiera wynik — dla trzech lig, także w podziale na siłę faworyta.

Dane wejściowe:
  data/{slug}_progress.csv         — pierwszy strzelec, wynik
  data/{POL,E0,P1}.csv             — kursy (Ekstraklasa: zamykające AvgC*, EPL/Portugalia: Avg*)
Output:
  csv/leagues/first_goal_favourite.csv        — odsetek „faworyt strzela pierwszy" per liga
  csv/leagues/first_goal_favourite_bands.csv  — j.w. w podziale na siłę faworyta
  figures/leagues/fig118_favourite_scores_first_leagues.png
  figures/leagues/fig119_favourite_first_by_strength_leagues.png
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

STRENGTH_BINS = [0, 0.45, 0.55, 1.0]
STRENGTH_LABELS = ["≤45%", "45–55%", "55%+"]


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
    inverse = 1 / merged[["odds_home", "odds_draw", "odds_away"]].to_numpy()
    normalized = inverse / inverse.sum(axis=1, keepdims=True)
    return pd.DataFrame({
        "favourite_first": merged["first_scorer"].to_numpy() == favourite_side,
        "favourite_prob": normalized[:, [0, 2]].max(axis=1),
    })


frames = {league: favourite_first_df(config) for league, config in LEAGUES.items()}

overall = pd.DataFrame({
    league: {"matches": len(frame), "favourite_first_pct": round(100 * frame["favourite_first"].mean(), 1)}
    for league, frame in frames.items()}).T.rename_axis("league").reset_index()

band_rows = []
for league, frame in frames.items():
    band = pd.cut(frame["favourite_prob"], bins=STRENGTH_BINS, labels=STRENGTH_LABELS)
    grouped = frame.groupby(band, observed=False)["favourite_first"]
    for label in STRENGTH_LABELS:
        group = frame[band == label]
        band_rows.append({"league": league, "strength": label, "matches": len(group),
                          "favourite_first_pct": round(100 * group["favourite_first"].mean(), 1)})
bands = pd.DataFrame(band_rows)

CSV_LEAGUES.mkdir(parents=True, exist_ok=True)
overall.to_csv(CSV_LEAGUES / "first_goal_favourite.csv", index=False)
bands.to_csv(CSV_LEAGUES / "first_goal_favourite_bands.csv", index=False)
print(overall.to_string(index=False))
print()
print(bands.to_string(index=False))

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

# ── fig119: faworyt strzela pierwszy wg siły faworyta ─────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(STRENGTH_LABELS))
width = 0.26
for offset, (league, config) in zip((-width, 0, width), LEAGUES.items()):
    values = [bands[(bands["league"] == league) & (bands["strength"] == label)]["favourite_first_pct"].iloc[0]
              for label in STRENGTH_LABELS]
    ax.bar(x + offset, values, width, color=config["color"], edgecolor="black", linewidth=0.5, label=league)
ax.axhline(50, color="#555", linestyle="--", linewidth=1.2)
ax.set_xticks(x)
ax.set_xticklabels(STRENGTH_LABELS)
ax.set_xlabel("Siła faworyta wg kursów (implikowane prawdopodobieństwo zwycięstwa)", fontsize=10)
ax.set_ylabel("Faworyt strzela pierwszy (%)", fontsize=11)
ax.set_ylim(0, 100)
ax.set_title("Im wyraźniejszy faworyt, tym częściej strzela pierwszy — poza Ekstraklasą (2025/26)",
             fontsize=12, weight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
clean_axes(ax)
fig.tight_layout()
save_figure(fig, "fig119_favourite_first_by_strength_leagues.png", output_dir=FIG_LEAGUES)
