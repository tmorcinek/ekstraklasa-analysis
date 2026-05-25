from pathlib import Path
import numpy as np
import pandas as pd

from ekstraklasa.config import LEAGUES, league_file, data_path, CURRENT_SEASON

ODD_COLS_EXTRA = ("PSCH", "PSCD", "PSCA", "B365CH", "B365CD", "B365CA",
                  "AvgCH", "AvgCD", "AvgCA", "MaxCH", "MaxCD", "MaxCA")


def _strip_bom(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lstrip("﻿") for c in df.columns]
    return df


def _coerce_ints(df: pd.DataFrame) -> pd.DataFrame:
    df["HG"] = df["HG"].astype(int)
    df["AG"] = df["AG"].astype(int)
    return df


def load_topfive(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _strip_bom(df)
    df = df.rename(columns={
        "HomeTeam": "Home", "AwayTeam": "Away",
        "FTHG": "HG", "FTAG": "AG", "FTR": "Res",
    })
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["HG", "AG", "Res", "Home", "Away"]).copy()
    df = _coerce_ints(df)
    for col in ODD_COLS_EXTRA:
        if col not in df.columns:
            df[col] = np.nan
    return df


def load_pol_all(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _strip_bom(df)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["HG", "AG", "Res", "Home", "Away", "Season"]).copy()
    df = _coerce_ints(df)
    return df


def load_pol_season(path: Path, season: str = CURRENT_SEASON) -> pd.DataFrame:
    return load_pol_all(path)[lambda d: d["Season"] == season].copy()


def load_league(name: str, season: str = CURRENT_SEASON) -> pd.DataFrame:
    if LEAGUES[name]["is_pol"]:
        return load_pol_season(league_file(name), season=season)
    return load_topfive(league_file(name))


def load_all_six_current() -> dict[str, pd.DataFrame]:
    return {name: load_league(name) for name in LEAGUES}


def load_pol_history() -> pd.DataFrame:
    return load_pol_all(data_path("POL.csv"))
