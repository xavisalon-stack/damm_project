"""Lectura, validación y regularización del histórico."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ESTABLISHMENT_COLUMN = "Establecimiento"
PRODUCT_COLUMN = "Material"
DATE_COLUMN = "Week-Month-Year"
TARGET_COLUMN = "CantidadUMB"
REQUIRED_COLUMNS = {
    ESTABLISHMENT_COLUMN,
    PRODUCT_COLUMN,
    DATE_COLUMN,
    TARGET_COLUMN,
}


def load_sales(path: str | Path) -> pd.DataFrame:
    """Carga la hoja de ventas sin modificar el fichero original."""
    frame = pd.read_excel(path, sheet_name="datos")
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing)}")

    frame = frame.copy()
    frame[DATE_COLUMN] = pd.to_datetime(frame[DATE_COLUMN], errors="raise")
    frame[TARGET_COLUMN] = pd.to_numeric(frame[TARGET_COLUMN], errors="raise")
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        nulls = frame[list(REQUIRED_COLUMNS)].isna().sum()
        raise ValueError(f"Hay nulos en columnas obligatorias: {nulls[nulls > 0].to_dict()}")
    if not frame[DATE_COLUMN].dt.dayofweek.eq(0).all():
        raise ValueError("La frecuencia esperada es semanal con fechas en lunes")
    return frame


def aggregate_weekly(frame: pd.DataFrame) -> pd.DataFrame:
    """Suma CantidadUMB sin mezclar establecimientos, productos ni semanas."""
    keys = [ESTABLISHMENT_COLUMN, PRODUCT_COLUMN, DATE_COLUMN]
    weekly = (
        frame.groupby(keys, as_index=False, observed=True)[TARGET_COLUMN]
        .sum()
        .sort_values(keys, kind="stable")
        .reset_index(drop=True)
    )
    return weekly


def regularize_weekly(weekly: pd.DataFrame, include_future: bool = False) -> pd.DataFrame:
    """Crea semanas regulares desde la primera observación de cada serie.

    La ausencia posterior a la primera compra se interpreta como cero porque el
    extracto semanal se considera completo. No se crean ceros antes de que la
    combinación establecimiento-producto aparezca por primera vez.
    """
    keys = [ESTABLISHMENT_COLUMN, PRODUCT_COLUMN]
    start = weekly.groupby(keys, observed=True)[DATE_COLUMN].min().rename("inicio")
    pairs = start.reset_index()
    final_date = weekly[DATE_COLUMN].max()
    if include_future:
        final_date += pd.Timedelta(days=7)
    dates = pd.DataFrame(
        {DATE_COLUMN: pd.date_range(weekly[DATE_COLUMN].min(), final_date, freq="7D")}
    )
    panel = pairs.merge(dates, how="cross")
    panel = panel.loc[panel[DATE_COLUMN].ge(panel["inicio"])].drop(columns="inicio")
    panel = panel.merge(weekly, on=keys + [DATE_COLUMN], how="left", validate="one_to_one")

    future_mask = panel[DATE_COLUMN].gt(weekly[DATE_COLUMN].max())
    panel.loc[~future_mask, TARGET_COLUMN] = panel.loc[~future_mask, TARGET_COLUMN].fillna(0.0)
    return panel.sort_values(keys + [DATE_COLUMN], kind="stable").reset_index(drop=True)
