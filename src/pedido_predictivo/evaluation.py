"""Métricas separadas por producto para no mezclar UMB incompatibles."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .data import ESTABLISHMENT_COLUMN, PRODUCT_COLUMN, TARGET_COLUMN


def grouped_metrics(
    frame: pd.DataFrame,
    predictions: np.ndarray,
    group_columns: list[str],
) -> pd.DataFrame:
    scored = frame[group_columns + [TARGET_COLUMN]].copy()
    scored["prediccion"] = predictions
    scored["error"] = scored["prediccion"] - scored[TARGET_COLUMN]
    scored["error_absoluto"] = scored["error"].abs()
    scored["objetivo_absoluto"] = scored[TARGET_COLUMN].abs()
    result = (
        scored.groupby(group_columns, observed=True)
        .agg(
            observaciones=(TARGET_COLUMN, "size"),
            mae=("error_absoluto", "mean"),
            error_absoluto_total=("error_absoluto", "sum"),
            objetivo_absoluto_total=("objetivo_absoluto", "sum"),
            sesgo=("error", "mean"),
            sesgo_total=("error", "sum"),
        )
        .reset_index()
    )
    denominator = result["objetivo_absoluto_total"].replace(0, np.nan)
    result["wape"] = result["error_absoluto_total"] / denominator
    result["sesgo_relativo"] = result["sesgo_total"] / denominator
    return result


def evaluation_summary(
    frame: pd.DataFrame,
    predictions: np.ndarray,
    method: str,
    split: str,
    fold: str,
) -> dict[str, object]:
    per_product = grouped_metrics(frame, predictions, [PRODUCT_COLUMN])
    valid = per_product["wape"].dropna()
    summary: dict[str, object] = {
        "split": split,
        "fold": fold,
        "metodo": method,
        "filas": len(frame),
        "productos": len(per_product),
        "productos_wape_evaluable": len(valid),
        "wape_macro_producto": valid.mean() if len(valid) else np.nan,
        "wape_mediana_producto": valid.median() if len(valid) else np.nan,
        "sesgo_relativo_macro_producto": per_product["sesgo_relativo"].mean(skipna=True),
    }
    segment = np.where(
        frame["purchase_frequency_13"].ge(0.5), "frecuente", "intermitente"
    )
    for name in ("frecuente", "intermitente"):
        mask = segment == name
        if not mask.any():
            summary[f"wape_macro_{name}"] = np.nan
            continue
        metrics = grouped_metrics(
            frame.loc[mask], np.asarray(predictions)[mask], [PRODUCT_COLUMN]
        )
        summary[f"wape_macro_{name}"] = metrics["wape"].mean(skipna=True)
    return summary


def detailed_test_metrics(
    frame: pd.DataFrame,
    predictions: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    by_product = grouped_metrics(frame, predictions, [PRODUCT_COLUMN])
    by_series = grouped_metrics(
        frame,
        predictions,
        [ESTABLISHMENT_COLUMN, PRODUCT_COLUMN],
    )
    return by_product, by_series
