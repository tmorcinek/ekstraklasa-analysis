"""Wykresy fig3, fig17, fig18 (Noll-Scully + ASD i NS Ekstraklasy w historii)."""
import _bootstrap  # noqa: F401

from ekstraklasa.config import LEAGUES, TOP5, CURRENT_SEASON, data_path
from ekstraklasa.data.loaders import load_topfive, load_pol_all
from ekstraklasa.data.tables import build_table
from ekstraklasa.plots.balance_figs import (
    fig3_noll_scully,
    fig17_asd_compare,
    fig18_ns_history,
)


def collect_2526() -> tuple[dict, "pd.DataFrame"]:
    leagues = {}
    for league in TOP5:
        matches = load_topfive(data_path(LEAGUES[league]["file"]))
        leagues[league] = {"matches": matches, "table": build_table(matches)}
    pol_all = load_pol_all(data_path("POL.csv"))
    current = pol_all[pol_all["Season"] == CURRENT_SEASON].copy()
    leagues["Ekstraklasa"] = {"matches": current, "table": build_table(current)}
    return leagues, pol_all


def main() -> None:
    leagues, pol_all = collect_2526()
    print("Figures:")
    fig3_noll_scully(leagues)
    fig17_asd_compare(leagues)
    fig18_ns_history(pol_all, leagues)
    print("Done.")


if __name__ == "__main__":
    main()
