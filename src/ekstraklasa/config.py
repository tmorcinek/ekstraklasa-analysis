from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CSV_DIR = OUTPUT_DIR / "csv"
FIG_DIR = OUTPUT_DIR / "figures"

# Figure subdirectories
FIG_BALANCE = FIG_DIR / "balance"
FIG_H2H = FIG_DIR / "h2h"
FIG_TEAMS = FIG_DIR / "teams"
FIG_LEAGUES = FIG_DIR / "leagues"
FIG_STYLE = FIG_DIR / "style"
FIG_STYLE_ESA = FIG_STYLE / "esa"

# CSV subdirectories
CSV_BALANCE = CSV_DIR / "balance"
CSV_MODEL = CSV_DIR / "model"
CSV_H2H = CSV_DIR / "h2h"
CSV_TEAMS = CSV_DIR / "teams"
CSV_STYLE = CSV_DIR / "style"
CSV_LEAGUES = CSV_DIR / "leagues"

for _d in [
    CSV_DIR, FIG_DIR,
    FIG_BALANCE, FIG_H2H, FIG_TEAMS, FIG_LEAGUES, FIG_STYLE, FIG_STYLE_ESA,
    CSV_BALANCE, CSV_MODEL, CSV_H2H, CSV_TEAMS, CSV_STYLE, CSV_LEAGUES,
]:
    _d.mkdir(parents=True, exist_ok=True)

LEAGUES: dict[str, dict] = {
    "Ekstraklasa": {"file": "POL.csv",  "color": "#d62728", "is_pol": True,  "games": 34, "tiebreak": "h2h"},
    "EPL":         {"file": "E0.csv",   "color": "#3b3b6d", "is_pol": False, "games": 38, "tiebreak": "simple"},
    "La Liga":     {"file": "SP1.csv",  "color": "#b88a0a", "is_pol": False, "games": 38, "tiebreak": "simple"},
    "Bundesliga":  {"file": "D1.csv",   "color": "#2a6f70", "is_pol": False, "games": 34, "tiebreak": "simple"},
    "Serie A":     {"file": "I1.csv",   "color": "#7a3b6d", "is_pol": False, "games": 38, "tiebreak": "simple"},
    "Ligue 1":     {"file": "F1.csv",   "color": "#4a7a3b", "is_pol": False, "games": 34, "tiebreak": "simple"},
}

COLORS: dict[str, str] = {name: meta["color"] for name, meta in LEAGUES.items()}

TOP5 = ["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
ALL_SIX = ["Bundesliga", "Serie A", "Ligue 1", "La Liga", "EPL", "Ekstraklasa"]

CURRENT_SEASON = "2025/2026"

TEAM_MAP: dict[str, str] = {
    "Bruk-Bet Termalica Nieciecza": "Termalica B-B.",
    "Cracovia": "Cracovia",
    "GKS Katowice": "GKS Katowice",
    "Górnik Zabrze": "Gornik Zabrze",
    "Jagiellonia Białystok": "Jagiellonia",
    "KS Lechia Gdańsk": "Lechia Gdansk",
    "Lech Poznań": "Lech Poznan",
    "Legia Warszawa": "Legia",
    "MKS Korona Kielce": "Korona Kielce",
    "MZKS Arka Gdynia": "Arka Gdynia",
    "Motor Lublin": "Motor Lublin",
    "Piast Gliwice": "Piast Gliwice",
    "Pogoń Szczecin": "Pogon Szczecin",
    "Radomiak Radom": "Radomiak Radom",
    "Raków Częstochowa": "Rakow",
    "Widzew Łódź": "Widzew Lodz",
    "Wisła Płock": "Wisla Plock",
    "Zagłębie Lubin": "Zaglebie",
}

STYLE_DATA_FILE = "ekstraklasa_25_26_statistics.csv"


def data_path(filename: str) -> Path:
    return DATA_DIR / filename


def league_file(league_name: str) -> Path:
    return DATA_DIR / LEAGUES[league_name]["file"]
