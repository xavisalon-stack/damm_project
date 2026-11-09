"""Entrenamiento, validación temporal, evaluación y generación de propuestas."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .commercial import build_proposals
from .data import DATE_COLUMN, TARGET_COLUMN, aggregate_weekly, load_sales, regularize_weekly
from .evaluation import detailed_test_metrics, evaluation_summary
from .features import build_features
from .models import (
    DirectQuantityModel,
    TwoStageQuantityModel,
    baseline_predictions,
)

MODEL_FACTORIES = {
    "modelo_global_directo": DirectQuantityModel,
    "modelo_global_dos_etapas": TwoStageQuantityModel,
}


def _fit_predict(
    method: str,
    train: pd.DataFrame,
    score: pd.DataFrame,
) -> tuple[np.ndarray, object | None]:
    if method in baseline_predictions(score):
        return baseline_predictions(score)[method], None
    model = MODEL_FACTORIES[method]().fit(train, TARGET_COLUMN)
    return model.predict(score), model


def _write_report(
    path: Path,
    comparison: pd.DataFrame,
    selected: str,
    dates: list[pd.Timestamp],
    forecast_date: pd.Timestamp,
    rows: int,
) -> None:
    validation = comparison.loc[comparison["split"].eq("validacion")]
    test = comparison.loc[comparison["split"].eq("prueba")].sort_values(
        "wape_macro_producto"
    )
    means = (
        validation.groupby("metodo")["wape_macro_producto"]
        .mean()
        .sort_values()
    )
    lines = [
        "# Informe del modelo predictivo",
        "",
        "## Objetivo",
        "",
        "Predecir la suma semanal de `CantidadUMB` por `Establecimiento` y `Material` "
        "para los próximos 7 días.",
        "",
        "El resultado es una **previsión de compra**, no una estimación de consumo real.",
        "",
        "## Preparación",
        "",
        f"- {rows:,} filas originales agregadas por establecimiento, material y semana.",
        "- Los valores negativos se conservaron al sumar; no se reinterpretaron sin un indicador documental.",
        "- Las ausencias se convirtieron en cero únicamente desde la primera aparición de cada serie.",
        "- Las variables históricas se desplazan al menos un periodo para evitar fuga futura.",
        "- No se mezclan productos al calcular métricas: WAPE y sesgo se calculan primero por material.",
        "- No se usa una referencia estacional anual: solo existe un año y no puede validarse.",
        "",
        "## Validación temporal",
        "",
        "- Cortes de validación: " + ", ".join(d.date().isoformat() for d in dates[:-4]) + ".",
        "- Prueba final: " + ", ".join(d.date().isoformat() for d in dates[-4:]) + ".",
        "- No se realizó división aleatoria.",
        "",
        "WAPE macro medio de validación por producto:",
        "",
        "| Método | WAPE macro |",
        "|---|---:|",
    ]
    for method, value in means.items():
        lines.append(f"| {method} | {value:.4f} |")
    lines.extend(
        [
            "",
            f"Modelo seleccionado: `{selected}`.",
            "",
            "La selección usa el menor WAPE macro por producto en validación, no la complejidad.",
            "",
            "Resultados en prueba final:",
            "",
            "| Método | WAPE macro | Frecuentes | Intermitentes |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in test.itertuples(index=False):
        lines.append(
            f"| {row.metodo} | {row.wape_macro_producto:.4f} | "
            f"{row.wape_macro_frecuente:.4f} | {row.wape_macro_intermitente:.4f} |"
        )
    test_best = test.iloc[0]["metodo"]
    selected_test = test.loc[test["metodo"].eq(selected)].iloc[0]
    lines.extend(
        [
            "",
            (
                f"En prueba, `{test_best}` obtiene el menor WAPE macro. "
                f"`{selected}` logra {selected_test['wape_macro_frecuente']:.4f} en series "
                f"frecuentes y {selected_test['wape_macro_intermitente']:.4f} en intermitentes."
            ),
            "La mejora observada en validación no es robusta en la prueba final; no se justifica "
            "atribuir una ganancia estable al aprendizaje automático.",
            "",
            "## Previsión",
            "",
            f"- Inicio del horizonte: {forecast_date.date().isoformat()}.",
            "- El pedido recomendado es orientativo e igual a la previsión: no se dispone de stock, "
            "entradas, mínimos ni conversiones comerciales.",
            "- La unidad de UMB no está confirmada y se deja vacía en la salida estructurada.",
            "",
            "## Limitaciones",
            "",
            "- Solo hay 52 semanas de 2025.",
            "- No se conocen altas, bajas ni descatalogaciones.",
            "- No hay identificador de documento en ventas para clasificar devoluciones o anulaciones.",
            "- El extracto termina mucho antes de la fecha de generación; las propuestas no deben "
            "usarse operativamente sin actualizar el histórico.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_training(data_path: str | Path, output_dir: str | Path) -> dict[str, object]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    raw = load_sales(data_path)
    weekly = aggregate_weekly(raw)
    panel = regularize_weekly(weekly, include_future=True)
    featured, product_mapping = build_features(panel)

    observed = featured.loc[featured[TARGET_COLUMN].notna()].copy()
    observed = observed.loc[observed["history_weeks"].ge(1)]
    dates = sorted(observed[DATE_COLUMN].unique())
    if len(dates) < 20:
        raise ValueError("Se necesitan al menos 20 periodos para esta validación temporal")
    validation_dates = [pd.Timestamp(dates[-13]), pd.Timestamp(dates[-9]), pd.Timestamp(dates[-5])]
    test_dates = [pd.Timestamp(date) for date in dates[-4:]]

    summaries: list[dict[str, object]] = []
    methods = ["ultima_cantidad", "media_movil_4", *MODEL_FACTORIES]
    for fold_date in validation_dates:
        train = observed.loc[observed[DATE_COLUMN].lt(fold_date)]
        score = observed.loc[observed[DATE_COLUMN].eq(fold_date)]
        for method in methods:
            prediction, _ = _fit_predict(method, train, score)
            summaries.append(
                evaluation_summary(
                    score,
                    prediction,
                    method,
                    "validacion",
                    fold_date.date().isoformat(),
                )
            )

    comparison = pd.DataFrame(summaries)
    selected = (
        comparison.loc[comparison["split"].eq("validacion")]
        .groupby("metodo")["wape_macro_producto"]
        .mean()
        .idxmin()
    )

    test_train = observed.loc[observed[DATE_COLUMN].lt(test_dates[0])]
    test = observed.loc[observed[DATE_COLUMN].isin(test_dates)]
    selected_test_prediction: np.ndarray | None = None
    for method in methods:
        prediction, _ = _fit_predict(method, test_train, test)
        comparison.loc[len(comparison)] = evaluation_summary(
            test, prediction, method, "prueba", "ultimas_4_semanas"
        )
        if method == selected:
            selected_test_prediction = prediction
    assert selected_test_prediction is not None

    by_product, by_series = detailed_test_metrics(test, selected_test_prediction)
    comparison.to_csv(output / "comparativa_modelos.csv", index=False)
    by_product.to_csv(output / "metricas_prueba_por_producto.csv", index=False)
    by_series.to_csv(output / "metricas_prueba_por_serie.csv", index=False)

    forecast = featured.loc[featured[TARGET_COLUMN].isna()].copy()
    final_prediction, final_model = _fit_predict(selected, observed, forecast)
    generated_at = pd.Timestamp.now(tz="Europe/Madrid")
    proposals = build_proposals(
        forecast,
        pd.Series(final_prediction, index=forecast.index),
        selected,
        generated_at,
    )
    proposals.to_csv(output / "previsiones_pedidos.csv", index=False)

    artifact = {
        "metodo": selected,
        "modelo": final_model,
        "product_mapping": product_mapping,
        "feature_columns_version": 1,
        "ultima_semana_observada": weekly[DATE_COLUMN].max(),
    }
    joblib.dump(artifact, output / "modelo.joblib", compress=3)
    _write_report(
        output / "informe_modelo.md",
        comparison,
        selected,
        validation_dates + test_dates,
        pd.Timestamp(forecast[DATE_COLUMN].min()),
        len(raw),
    )
    return {
        "metodo_seleccionado": selected,
        "inicio_horizonte": pd.Timestamp(forecast[DATE_COLUMN].min()).date().isoformat(),
        "fin_horizonte": (
            pd.Timestamp(forecast[DATE_COLUMN].min()) + pd.Timedelta(days=6)
        ).date().isoformat(),
        "propuestas": len(proposals),
        "salida": str(output),
    }
