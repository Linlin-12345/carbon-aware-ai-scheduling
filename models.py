"""
models.py
---------
Training and evaluation pipeline for carbon exposure prediction.

Models:
    - Naive persistence baseline (lag-1h)
    - Linear Regression
    - Random Forest (selected model)
    - XGBoost
    - Day-ahead Random Forest (no lag-1h)
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


# Features used in short-term model
SHORT_TERM_FEATURES = [
    "carbon_proxy_lag1h",
    "carbon_proxy_lag24h",
    "carbon_proxy_lag168h",
    "hour_utc",
    "weekday",
    "month",
    "demand_mw",
    "demand_lag1h",
]

# Features used in day-ahead model (lag-1h and contemporaneous demand removed)
DAY_AHEAD_FEATURES = [
    "carbon_proxy_lag24h",
    "carbon_proxy_lag168h",
    "hour_utc",
    "weekday",
    "month",
]


def chronological_split(df: pd.DataFrame, datetime_col: str = "UTC_time", test_months: int = 3):
    """
    Split data chronologically to avoid leakage on autocorrelated series.
    Default: Jan–Sep training, Oct–Dec test (for full-year 2025 data).
    """
    df = df.sort_values(datetime_col)
    cutoff = df[datetime_col].max() - pd.DateOffset(months=test_months)
    train = df[df[datetime_col] <= cutoff]
    test = df[df[datetime_col] > cutoff]
    return train, test


def evaluate(y_true, y_pred, label: str = "") -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    if label:
        print(f"[{label}] MAE={mae:.4f}  RMSE={rmse:.4f}")
    return {"model": label, "MAE": mae, "RMSE": rmse}


def run_models(train: pd.DataFrame, test: pd.DataFrame, target: str = "carbon_proxy") -> pd.DataFrame:
    """
    Train and evaluate all models. Returns a summary DataFrame.
    """
    results = []

    # Drop rows with NaN in features
    train_st = train.dropna(subset=SHORT_TERM_FEATURES + [target])
    test_st = test.dropna(subset=SHORT_TERM_FEATURES + [target])

    X_train = train_st[SHORT_TERM_FEATURES]
    y_train = train_st[target]
    X_test = test_st[SHORT_TERM_FEATURES]
    y_test = test_st[target]

    # 1. Naive baseline: predict next hour = current hour (lag-1h)
    y_naive = test_st["carbon_proxy_lag1h"]
    results.append(evaluate(y_test, y_naive, "Naive (lag-1h)"))

    # 2. Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    results.append(evaluate(y_test, lr.predict(X_test), "Linear Regression"))

    # 3. Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    results.append(evaluate(y_test, rf.predict(X_test), "Random Forest"))

    # 4. XGBoost
    xgb = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    xgb.fit(X_train, y_train)
    results.append(evaluate(y_test, xgb.predict(X_test), "XGBoost"))

    # 5. Day-ahead RF (no lag-1h)
    train_da = train.dropna(subset=DAY_AHEAD_FEATURES + [target])
    test_da = test.dropna(subset=DAY_AHEAD_FEATURES + [target])
    rf_da = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_da.fit(train_da[DAY_AHEAD_FEATURES], train_da[target])
    y_da_naive = test_da["carbon_proxy_lag24h"]
    results.append(evaluate(test_da[target], y_da_naive, "Day-ahead Naive (lag-24h)"))
    results.append(evaluate(test_da[target], rf_da.predict(test_da[DAY_AHEAD_FEATURES]), "Day-ahead RF"))

    return pd.DataFrame(results), rf, rf_da


def get_feature_importance(rf_model, feature_names: list) -> pd.DataFrame:
    """Extract and sort Random Forest feature importances."""
    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": rf_model.feature_importances_
    }).sort_values("importance", ascending=False)
    return fi
