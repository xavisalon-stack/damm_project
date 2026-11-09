"""Variables históricas calculadas exclusivamente con periodos anteriores."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .data import DATE_COLUMN, ESTABLISHMENT_COLUMN, PRODUCT_COLUMN, TARGET_COLUMN

FEATURE_COLUMNS = [
    "product_code",
    "lag_1",
    "lag_2",
    "lag_4",
    "lag_13",
    "rolling_mean_4",
    "rolling_mean_13",
    "rolling_std_4",
    "trend_4_13",
    "purchase_frequency_4",
    "purchase_frequency_13",
    "purchase_frequency_history",
    "weeks_since_purchase",
    "history_weeks",
    "week_sin",
    "week_cos",
    "month_sin",
    "month_cos",
]


def build_features(
    panel: pd.DataFrame,
    product_mapping: dict[str, int] | None = None,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Añade lags y estadísticas desplazadas para impedir fuga temporal."""
    data = panel.copy()
    keys = [ESTABLISHMENT_COLUMN, PRODUCT_COLUMN]
    data = data.sort_values(keys + [DATE_COLUMN], kind="stable").reset_index(drop=True)
    grouped = data.groupby(keys, sort=False, observed=True)[TARGET_COLUMN]

    lags = {period: grouped.shift(period) for period in range(1, 14)}
    for period in (1, 2, 4, 13):
        data[f"lag_{period}"] = lags[period].fillna(0.0)

    lag4 = pd.concat([lags[i] for i in range(1, 5)], axis=1)
    lag13 = pd.concat([lags[i] for i in range(1, 14)], axis=1)
    data["rolling_mean_4"] = lag4.mean(axis=1).fillna(0.0)
    data["rolling_mean_13"] = lag13.mean(axis=1).fillna(0.0)
    data["rolling_std_4"] = lag4.std(axis=1, ddof=0).fillna(0.0)
    data["trend_4_13"] = data["rolling_mean_4"] - data["rolling_mean_13"]
    data["purchase_frequency_4"] = lag4.gt(0).sum(axis=1) / lag4.notna().sum(axis=1).clip(lower=1)
    data["purchase_frequency_13"] = lag13.gt(0).sum(axis=1) / lag13.notna().sum(axis=1).clip(lower=1)

    history_weeks = data.groupby(keys, sort=False, observed=True).cumcount()
    positive = data[TARGET_COLUMN].gt(0).astype("int16")
    past_positive = positive.groupby(
        [data[ESTABLISHMENT_COLUMN], data[PRODUCT_COLUMN]], sort=False
    ).cumsum() - positive
    data["history_weeks"] = history_weeks
    data["purchase_frequency_history"] = (
        past_positive / history_weeks.replace(0, np.nan)
    ).fillna(0.0)

    positive_date = data[DATE_COLUMN].where(data[TARGET_COLUMN].gt(0))
    last_positive = positive_date.groupby(
        [data[ESTABLISHMENT_COLUMN], data[PRODUCT_COLUMN]], sort=False
    ).ffill()
    previous_positive = last_positive.groupby(
        [data[ESTABLISHMENT_COLUMN], data[PRODUCT_COLUMN]], sort=False
    ).shift(1)
    data["weeks_since_purchase"] = (
        (data[DATE_COLUMN] - previous_positive).dt.days.div(7).fillna(history_weeks + 1)
    )

    products = data[PRODUCT_COLUMN].astype(str)
    if product_mapping is None:
        product_mapping = {
            product: code for code, product in enumerate(sorted(products.unique()))
        }
    unknown_code = len(product_mapping)
    data["product_code"] = products.map(product_mapping).fillna(unknown_code).astype("int16")

    iso_week = data[DATE_COLUMN].dt.isocalendar().week.astype(float)
    month = data[DATE_COLUMN].dt.month.astype(float)
    data["week_sin"] = np.sin(2 * np.pi * iso_week / 52.0)
    data["week_cos"] = np.cos(2 * np.pi * iso_week / 52.0)
    data["month_sin"] = np.sin(2 * np.pi * month / 12.0)
    data["month_cos"] = np.cos(2 * np.pi * month / 12.0)
    return data, product_mapping
