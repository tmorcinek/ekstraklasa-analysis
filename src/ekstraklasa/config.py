from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CSV_DIR = OUTPUT_DIR / "csv"
FIG_DIR = OUTPUT_DIR / "figures"

CSV_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

LEAGUES: dict[str, dict] = {
    "Ekstraklasa": {"file": "POL.csv",  "color": "#d62728", "is_pol": True,  "games": 34},
    "EPL":         {"file": "E0.csv",   "color": "#3b3b6d", "is_pol": False, "games": 38},
    "La Liga":     {"file": "SP1.csv",  "color": "#b88a0a", "is_pol": False, "games": 38},
    "Bundesliga":  {"file": "D1.csv",   "color": "#2a6f70", "is_pol": False, "games": 34},
    "Serie A":     {"file": "I1.csv",   "color": "#7a3b6d", "is_pol": False, "games": 38},
    "Ligue 1":     {"file": "F1.csv",   "color": "#4a7a3b", "is_pol": False, "games": 34},
}

COLORS: dict[str, str] = {name: meta["color"] for name, meta in LEAGUES.items()}

TOP5 = ["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
ALL_SIX = ["Bundesliga", "Serie A", "Ligue 1", "La Liga", "EPL", "Ekstraklasa"]

CURRENT_SEASON = "2025/2026"


def data_path(filename: str) -> Path:
    return DATA_DIR / filename


def league_file(league_name: str) -> Path:
    return DATA_DIR / LEAGUES[league_name]["file"]
