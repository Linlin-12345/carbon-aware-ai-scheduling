"""
carbon_proxy.py
---------------
Constructs the hourly carbon exposure proxy used throughout this project.

Carbon Proxy = (Coal + Gas + Petroleum) / Net Generation

This is a relative fossil-share indicator (0–1), consistent with
output-based emissions logic from Khan, Jack & Stephenson (2018).
It does NOT differentiate between coal and natural gas emissions factors.
"""

import pandas as pd
import numpy as np


# EIA Form 930 column name mapping (adjusted generation columns)
FOSSIL_COLS = {
    "coal": "NG_COL_UTS_H",       # Coal generation (MWh)
    "gas": "NG_NG_UTS_H",         # Natural gas generation (MWh)
    "petroleum": "NG_OIL_UTS_H",  # Petroleum generation (MWh)
}
NET_GEN_COL = "NG_TOT_UTS_H"      # Total net generation (MWh)
DEMAND_COL = "D_UTS_H"            # Total demand / load (MWh)


def build_carbon_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the hourly carbon exposure proxy for each BA-hour row.

    Parameters
    ----------
    df : pd.DataFrame
        Raw EIA Form 930 BALANCE dataframe with adjusted generation columns.

    Returns
    -------
    pd.DataFrame with added columns:
        - fossil_mwh     : sum of coal + gas + petroleum generation
        - carbon_proxy   : fossil_mwh / net_generation (clipped 0–1)
        - demand_mw      : electricity demand
    """
    df = df.copy()

    # Treat absent fuel types as 0 (not missing operational data)
    for col in FOSSIL_COLS.values():
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0).clip(lower=0)

    df["fossil_mwh"] = (
        df[FOSSIL_COLS["coal"]]
        + df[FOSSIL_COLS["gas"]]
        + df[FOSSIL_COLS["petroleum"]]
    )

    net_gen = df[NET_GEN_COL].replace(0, np.nan)
    df["carbon_proxy"] = (df["fossil_mwh"] / net_gen).clip(0, 1)

    if DEMAND_COL in df.columns:
        df["demand_mw"] = df[DEMAND_COL].fillna(np.nan)

    return df


def add_time_features(df: pd.DataFrame, datetime_col: str = "UTC_time") -> pd.DataFrame:
    """
    Add temporal features used in predictive modelling.

    Adds: hour_utc, hour_local (approximated), weekday, month, is_weekend
    """
    df = df.copy()
    dt = pd.to_datetime(df[datetime_col], utc=True)

    df["hour_utc"] = dt.dt.hour
    df["weekday"] = dt.dt.dayofweek        # 0=Monday, 6=Sunday
    df["month"] = dt.dt.month
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)

    return df


def add_lag_features(
    df: pd.DataFrame,
    group_col: str = "balancing_authority",
    proxy_col: str = "carbon_proxy",
    lags: list[int] = [1, 24, 168],
) -> pd.DataFrame:
    """
    Add lagged carbon proxy values within each balancing authority.

    Parameters
    ----------
    lags : list of ints
        Lag periods in hours. Default: 1h, 24h (same time yesterday), 168h (same time last week).
    """
    df = df.copy().sort_values([group_col, "UTC_time"])

    for lag in lags:
        col_name = f"carbon_proxy_lag{lag}h"
        df[col_name] = df.groupby(group_col)[proxy_col].shift(lag)

    return df
