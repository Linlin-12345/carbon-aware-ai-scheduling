"""
scheduler_sim.py
----------------
Simulates carbon exposure under four workload scheduling strategies:

    1. Baseline       — execute immediately at the nearest/default region
    2. Time-shift     — defer within the same region to lowest-carbon window
    3. Location-shift — route to the lowest-carbon region at the same time
    4. Joint opt.     — defer AND route to minimise carbon exposure

Produces the scenario comparison table in Section 6 of the report.
"""

import pandas as pd
import numpy as np


def simulate_scheduling(
    df: pd.DataFrame,
    proxy_col: str = "carbon_proxy",
    region_col: str = "eia_region",
    hour_col: str = "hour_utc",
    flexibility_hours: int = 12,
    batch_fraction: float = 0.70,
) -> pd.DataFrame:
    """
    Simulate four scheduling strategies and compare mean carbon exposure.

    Parameters
    ----------
    df : pd.DataFrame
        BA-hour dataframe with carbon_proxy and region labels.
    flexibility_hours : int
        Max hours a batch job can be deferred (time-shifting window).
    batch_fraction : float
        Fraction of workload that is flexible (not latency-bound).

    Returns
    -------
    pd.DataFrame with columns [strategy, mean_carbon_proxy, relative_reduction]
    """
    results = []

    # Regional mean profiles
    region_means = df.groupby(region_col)[proxy_col].mean()
    hourly_profiles = df.groupby([region_col, hour_col])[proxy_col].mean().reset_index()

    # ── 1. Baseline: immediate execution, no routing optimisation ──
    baseline = df[proxy_col].mean()
    results.append({"strategy": "Baseline (no optimisation)", "mean_carbon_proxy": baseline})

    # ── 2. Time-shift: defer within each region to best window ──
    def best_window_mean(group):
        """Return the mean proxy of the lowest-carbon flexibility_hours window."""
        vals = group[proxy_col].values
        if len(vals) < flexibility_hours:
            return vals.min()
        rolling_means = pd.Series(vals).rolling(flexibility_hours).mean().dropna()
        return rolling_means.min()

    time_shift_mean = (
        df.groupby([region_col, df.index // 24])
        .apply(best_window_mean)
        .mean()
    )
    # Blend with latency-bound fraction staying at baseline
    time_shift_blended = (
        batch_fraction * time_shift_mean + (1 - batch_fraction) * baseline
    )
    results.append({"strategy": f"Time-shift (±{flexibility_hours}h window)", "mean_carbon_proxy": time_shift_blended})

    # ── 3. Location-shift: route flexible jobs to cleanest region ──
    cleanest_region = region_means.idxmin()
    cleanest_mean = region_means.min()
    location_shift_blended = (
        batch_fraction * cleanest_mean + (1 - batch_fraction) * baseline
    )
    results.append({
        "strategy": f"Location-shift (route to {cleanest_region})",
        "mean_carbon_proxy": location_shift_blended
    })

    # ── 4. Joint optimisation: best region × best time window ──
    best_hourly = hourly_profiles.loc[
        hourly_profiles.groupby(region_col)[proxy_col].idxmin()
    ]
    joint_best = best_hourly[proxy_col].min()
    joint_blended = (
        batch_fraction * joint_best + (1 - batch_fraction) * baseline
    )
    results.append({
        "strategy": "Joint optimisation (location + time)",
        "mean_carbon_proxy": joint_blended
    })

    result_df = pd.DataFrame(results)
    result_df["relative_reduction_pct"] = (
        (baseline - result_df["mean_carbon_proxy"]) / baseline * 100
    ).round(1)

    return result_df


def regional_scheduling_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-region: show hourly spread, weekend advantage, and scheduling potential.
    Matches Table 2 in the report.
    """
    hourly = df.groupby(["eia_region", "hour_utc"])["carbon_proxy"].mean()
    spread = hourly.groupby("eia_region").agg(lambda x: (x.max() - x.min()) * 100).rename("hourly_spread_pp")

    weekday_mean = df[df["is_weekend"] == 0].groupby("eia_region")["carbon_proxy"].mean()
    weekend_mean = df[df["is_weekend"] == 1].groupby("eia_region")["carbon_proxy"].mean()
    weekend_advantage = ((weekday_mean - weekend_mean) * 100).rename("weekend_advantage_pp")

    summary = pd.concat([spread, weekend_advantage], axis=1).reset_index()
    summary = summary.sort_values("hourly_spread_pp", ascending=False)
    return summary
