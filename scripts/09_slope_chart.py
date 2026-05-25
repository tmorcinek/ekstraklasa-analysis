"""Slope chart pozycji drużyn Ekstraklasy 2024/25 → 2025/26.

Output: fig16
"""
import _bootstrap  # noqa: F401

from ekstraklasa.config import CURRENT_SEASON, data_path
from ekstraklasa.data.loaders import load_pol_season
from ekstraklasa.metrics.positions import position_changes
from ekstraklasa.plots.slope_fig import fig_slope_chart


DISPLAY_NAMES = {
    "Lech Poznan": "Lech Poznań",
    "Gornik Zabrze": "Górnik Zabrze",
    "Rakow": "Raków",
    "Zaglebie": "Zagłębie Lubin",
    "Wisla Plock": "Wisła Płock",
    "Radomiak Radom": "Radomiak",
    "Lechia Gdansk": "Lechia Gdańsk*",
    "Pogon Szczecin": "Pogoń Szczecin",
    "Widzew Lodz": "Widzew Łódź",
}


def main() -> None:
    prev_matches = load_pol_season(data_path("POL.csv"), season="2024/2025")
    curr_matches = load_pol_season(data_path("POL.csv"), season=CURRENT_SEASON)
    changes = position_changes(prev_matches, curr_matches, n_relegated=3)
    fig_slope_chart(
        changes,
        league_name="Ekstraklasa",
        prev_season="2024/25",
        curr_season="2025/26",
        output_name="fig16_slope_chart.png",
        name_map=DISPLAY_NAMES,
    )


if __name__ == "__main__":
    main()
