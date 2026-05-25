import numpy as np
import pandas as pd

ODDS_SOURCES: tuple[tuple[str, str, str], ...] = (
    ("AvgCH", "AvgCD", "AvgCA"),
    ("B365CH", "B365CD", "B365CA"),
    ("PSCH", "PSCD", "PSCA"),
)


def implied_probs(odds_h: float, odds_d: float, odds_a: float) -> np.ndarray | None:
    """Decimal odds → no-vig probabilities via proportional renormalization."""
    if not (odds_h > 1 and odds_d > 1 and odds_a > 1):
        return None
    raw = np.array([1 / odds_h, 1 / odds_d, 1 / odds_a])
    return raw / raw.sum()


def select_odds_source(matches: pd.DataFrame, min_rows: int = 10) -> tuple[str, str, str] | None:
    """Pick the first odds triple available with enough non-null rows."""
    for cols in ODDS_SOURCES:
        if all(col in matches.columns for col in cols):
            valid = matches.dropna(subset=list(cols))
            if len(valid) > min_rows:
                return cols
    return None


def probabilities_matrix(matches: pd.DataFrame, cols: tuple[str, str, str]) -> tuple[np.ndarray, np.ndarray]:
    """Return (P, y) where P is (N,3) implied probs and y is encoded outcome (0=H, 1=D, 2=A)."""
    subset = matches.dropna(subset=list(cols)).copy()
    odds_h = subset[cols[0]].astype(float).values
    odds_d = subset[cols[1]].astype(float).values
    odds_a = subset[cols[2]].astype(float).values
    raw = np.vstack([1 / odds_h, 1 / odds_d, 1 / odds_a]).T
    probs = raw / raw.sum(axis=1, keepdims=True)
    outcomes = subset["Res"].map({"H": 0, "D": 1, "A": 2}).values
    return probs, outcomes


def predictability_metrics(matches: pd.DataFrame) -> dict:
    """Brier, log-loss, upset rate using the best available odds source."""
    out = {"n_used": 0, "brier": float("nan"), "log_loss": float("nan"),
           "upset_rate": float("nan"), "fav_winrate": float("nan"), "src": "none"}

    chosen = select_odds_source(matches)
    if chosen is None:
        return out

    rows, actual = [], []
    for _, row in matches.iterrows():
        try:
            probs = implied_probs(float(row[chosen[0]]), float(row[chosen[1]]), float(row[chosen[2]]))
        except (ValueError, TypeError):
            probs = None
        if probs is None:
            continue
        rows.append(probs)
        actual.append({"H": 0, "D": 1, "A": 2}[row["Res"]])

    if not rows:
        return out

    probs_matrix = np.vstack(rows)
    outcomes = np.array(actual)
    onehot = np.zeros_like(probs_matrix)
    onehot[np.arange(len(outcomes)), outcomes] = 1
    eps = 1e-12

    out["src"] = chosen[0]
    out["n_used"] = len(outcomes)
    out["brier"] = float(np.mean(np.sum((probs_matrix - onehot) ** 2, axis=1)))
    out["log_loss"] = float(-np.mean(np.log(probs_matrix[np.arange(len(outcomes)), outcomes] + eps)))
    favourite = probs_matrix.argmax(axis=1)
    out["fav_winrate"] = float((favourite == outcomes).mean())
    out["upset_rate"] = 1.0 - out["fav_winrate"]
    return out
