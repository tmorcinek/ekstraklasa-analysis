"""Dixon-Coles (Maher) fit + Monte Carlo dla 6 lig.

Output: output/csv/dixon_coles_metrics.csv, fig6, fig7
"""
import _bootstrap  # noqa: F401

import numpy as np
import pandas as pd

from ekstraklasa.config import CSV_DIR, LEAGUES, TOP5, data_path
from ekstraklasa.data.loaders import load_topfive, load_pol_season
from ekstraklasa.data.tables import points_by_team
from ekstraklasa.metrics.dixon_coles import fit_maher, simulate_season
from ekstraklasa.plots.dc_figs import fig6_mc_distributions, fig7_team_strengths


def load_current() -> dict[str, pd.DataFrame]:
    leagues = {}
    for league in TOP5:
        matches = load_topfive(data_path(LEAGUES[league]["file"]))
        leagues[league] = matches[["Home", "Away", "HG", "AG", "Res"]]
    leagues["Ekstraklasa"] = load_pol_season(data_path("POL.csv"))[["Home", "Away", "HG", "AG", "Res"]]
    return leagues


def main() -> None:
    leagues = load_current()
    rows = []
    sim_data = {}
    np.random.seed(42)

    for name, matches in leagues.items():
        print(f"\n=== {name} ({len(matches)} matches) ===")
        params = fit_maher(matches, n_iter=300)
        att, defense, gamma = params["att"], params["def"], params["gamma"]
        teams = params["teams"]

        strength = att + defense
        sd_strength = float(np.std(strength, ddof=0))

        obs_points, games = points_by_team(matches, teams)
        ppg = obs_points / np.maximum(games, 1)
        r2 = float(np.corrcoef(strength, ppg)[0, 1]) ** 2 if np.std(strength) > 0 else float("nan")

        obs_asd = float(np.std(obs_points, ddof=0))
        sims = simulate_season(att, defense, gamma, n_sims=5000, seed=42)
        sim_asd = sims.std(axis=1, ddof=0)
        mc_mean = float(sim_asd.mean())
        mc_p_low = float((sim_asd <= obs_asd).mean())
        pred_pts = sims.mean(axis=0)
        pred_asd = float(np.std(pred_pts, ddof=0))

        print(f"  γ (home adv): {gamma:.3f}")
        print(f"  SD(strength): {sd_strength:.3f}")
        print(f"  R²(strength → PPG): {r2:.3f}")
        print(f"  Observed ASD: {obs_asd:.2f}")
        print(f"  MC mean ASD ({len(sim_asd)} sims): {mc_mean:.2f}")
        print(f"  MC P(ASD <= obs): {mc_p_low:.3f}")
        print(f"  Predicted (mean over sims) ASD: {pred_asd:.2f}")

        rows.append({
            "League": name,
            "N_matches_fit": len(matches),
            "Home_adv_gamma": gamma,
            "SD_strength": sd_strength,
            "R2_strength_PPG": r2,
            "Obs_ASD": obs_asd,
            "MC_mean_ASD": mc_mean,
            "MC_p_value_low": mc_p_low,
            "MC_pred_ASD_from_means": pred_asd,
        })
        sim_data[name] = {
            "obs_asd": obs_asd, "sim_asd": sim_asd, "obs_pts": obs_points,
            "teams": teams, "strength": strength, "ppg": ppg,
        }

    metrics = pd.DataFrame(rows).sort_values("SD_strength").reset_index(drop=True)
    metrics_path = CSV_DIR / "dixon_coles_metrics.csv"
    metrics.to_csv(metrics_path, index=False)
    print(f"\nWrote {metrics_path}")

    print("\n=== Cross-league summary (sorted by SD_strength) ===")
    with pd.option_context("display.float_format", "{:.3f}".format):
        print(metrics.to_string(index=False))

    fig6_mc_distributions(sim_data)
    fig7_team_strengths(sim_data)


if __name__ == "__main__":
    main()
