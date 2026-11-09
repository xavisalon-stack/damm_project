"""Reglas comerciales separadas de la previsión estadística."""

from __future__ import annotations

import math

import pandas as pd

from .data import DATE_COLUMN, ESTABLISHMENT_COLUMN, PRODUCT_COLUMN


def round_to_multiple(quantity: float, multiple: float | None) -> float:
    """Redondea hacia arriba solo cuando existe una conversión válida."""
    if multiple is None:
        return float(quantity)
    if multiple <= 0:
        raise ValueError("El múltiplo comercial debe ser positivo")
    return float(math.ceil(max(quantity, 0.0) / multiple) * multiple)


def build_proposals(
    forecast_rows: pd.DataFrame,
    predictions: pd.Series,
    method: str,
    generated_at: pd.Timestamp,
) -> pd.DataFrame:
    """Crea propuestas orientativas; no presupone stock, cajas ni palés."""
    result = forecast_rows[
        [
            ESTABLISHMENT_COLUMN,
            PRODUCT_COLUMN,
            DATE_COLUMN,
            "history_weeks",
            "weeks_since_purchase",
        ]
    ].copy()
    result["fecha_generacion"] = generated_at.date().isoformat()
    result["inicio_horizonte"] = result[DATE_COLUMN].dt.date.astype(str)
    result["fin_horizonte"] = (
        result[DATE_COLUMN] + pd.Timedelta(days=6)
    ).dt.date.astype(str)
    result["CantidadUMB_prevista"] = predictions.clip(lower=0).to_numpy()
    result["unidad_medida"] = pd.NA
    result["pedido_recomendado"] = result["CantidadUMB_prevista"]
    result["unidad_comercial"] = pd.NA
    result["conversion_aplicada"] = pd.NA
    result["metodo"] = method

    stale_history = generated_at.date() > forecast_rows[DATE_COLUMN].min().date()
    warnings = []
    for row in result.itertuples(index=False):
        items = ["stock_desconocido", "unidad_UMB_no_confirmada"]
        if stale_history:
            items.append("historico_desactualizado")
        if row.history_weeks < 4:
            items.append("historico_insuficiente")
        if row.weeks_since_purchase > 13:
            items.append("compra_muy_intermitente_o_producto_inactivo")
        warnings.append(";".join(items))
    result["advertencias"] = warnings
    return result.drop(
        columns=[DATE_COLUMN, "history_weeks", "weeks_since_purchase"]
    ).sort_values([ESTABLISHMENT_COLUMN, PRODUCT_COLUMN])


def proposal_message(proposals: pd.DataFrame, establishment: int | str) -> str:
    """Redacta una propuesta revisable sin enviar ni crear pedidos."""
    selected = proposals.loc[
        proposals[ESTABLISHMENT_COLUMN].astype(str).eq(str(establishment))
    ]
    if selected.empty:
        raise ValueError(f"No hay propuesta para el establecimiento {establishment}")
    lines = [
        f"Propuesta orientativa para el establecimiento {establishment},",
        "basada exclusivamente en su histórico de compras:",
    ]
    for row in selected.itertuples(index=False):
        lines.append(
            f"- Producto {getattr(row, PRODUCT_COLUMN)}: "
            f"{row.pedido_recomendado:.2f} UMB (unidad pendiente de confirmar)."
        )
    lines.append("Por favor, confirme o modifique las cantidades antes de tramitar el pedido.")
    return "\n".join(lines)
