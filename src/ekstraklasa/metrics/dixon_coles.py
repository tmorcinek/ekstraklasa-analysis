import numpy as np
import pandas as pd


def fit_maher(matches: pd.DataFrame, n_iter: int = 300, tol: float = 1e-6, verbose: bool = False) -> dict:
    """Fit Maher-style Poisson model (attack/defence/home advantage) via closed-form coordinate updates.

    Model: λ_home = exp(att_h - def_a + γ), λ_away = exp(att_a - def_h). Goals ~ Poisson(λ).
    Constraints: mean(att) = 0, mean(def) = 0.
    """
    teams = sorted(set(matches["Home"]).union(set(matches["Away"])))
    n_teams = len(teams)
    idx = {team: i for i, team in enumerate(teams)}

    home_idx = matches["Home"].map(idx).values
    away_idx = matches["Away"].map(idx).values
    home_goals = matches["HG"].values.astype(float)
    away_goals = matches["AG"].values.astype(float)

    scored = np.zeros(n_teams)
    conceded = np.zeros(n_teams)
    np.add.at(scored, home_idx, home_goals)
    np.add.at(scored, away_idx, away_goals)
    np.add.at(conceded, home_idx, away_goals)
    np.add.at(conceded, away_idx, home_goals)

    att = np.zeros(n_teams)
    defense = np.zeros(n_teams)
    gamma = 0.3
    prev_ll = -np.inf
    eps = 1e-9
    final_iter = 0

    for iteration in range(n_iter):
        denom_gamma = np.exp(att[home_idx] - defense[away_idx]).sum()
        if denom_gamma > 0 and home_goals.sum() > 0:
            gamma = float(np.log(home_goals.sum() / denom_gamma))

        denom_att = np.zeros(n_teams)
        np.add.at(denom_att, home_idx, np.exp(gamma - defense[away_idx]))
        np.add.at(denom_att, away_idx, np.exp(-defense[home_idx]))
        new_att = np.log((scored + eps) / (denom_att + eps))
        att = new_att - new_att.mean()

        num_def = np.zeros(n_teams)
        np.add.at(num_def, home_idx, np.exp(att[away_idx]))
        np.add.at(num_def, away_idx, np.exp(att[home_idx] + gamma))
        new_def = np.log((num_def + eps) / (conceded + eps))
        defense = new_def - new_def.mean()

        lam_home = np.exp(att[home_idx] - defense[away_idx] + gamma)
        lam_away = np.exp(att[away_idx] - defense[home_idx])
        log_lik = float(np.sum(-lam_home + home_goals * np.log(lam_home + 1e-12)
                               - lam_away + away_goals * np.log(lam_away + 1e-12)))
        if verbose and iteration % 20 == 0:
            print(f"  iter {iteration:3d}  ll={log_lik:.2f}  gamma={gamma:.3f}  "
                  f"SD_str={(att + defense).std():.3f}")
        final_iter = iteration + 1
        if abs(log_lik - prev_ll) < tol and iteration > 5:
            break
        prev_ll = log_lik

    return {
        "teams": teams,
        "att": att,
        "def": defense,
        "gamma": float(gamma),
        "n_iter": final_iter,
        "log_lik": log_lik,
        "idx": idx,
        "n_matches": len(matches),
    }


def simulate_season(att: np.ndarray, defense: np.ndarray, gamma: float,
                    n_sims: int = 5000, seed: int = 42) -> np.ndarray:
    """Simulate full double round-robin n_sims times. Returns (n_sims, n_teams) points matrix."""
    rng = np.random.default_rng(seed)
    n_teams = len(att)
    home_idx, away_idx = [], []
    for i in range(n_teams):
        for j in range(n_teams):
            if i == j:
                continue
            home_idx.append(i)
            away_idx.append(j)
    home_idx = np.array(home_idx)
    away_idx = np.array(away_idx)

    lam_home = np.exp(att[home_idx] - defense[away_idx] + gamma)
    lam_away = np.exp(att[away_idx] - defense[home_idx])

    points = np.zeros((n_sims, n_teams))
    for sim in range(n_sims):
        sim_home_goals = rng.poisson(lam_home)
        sim_away_goals = rng.poisson(lam_away)
        diff = sim_home_goals - sim_away_goals
        home_pts = np.where(diff > 0, 3, np.where(diff == 0, 1, 0))
        away_pts = np.where(diff < 0, 3, np.where(diff == 0, 1, 0))
        np.add.at(points[sim], home_idx, home_pts)
        np.add.at(points[sim], away_idx, away_pts)
    return points
