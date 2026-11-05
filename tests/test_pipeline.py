import pandas as pd
import pytest

from pedido_predictivo.commercial import round_to_multiple
from pedido_predictivo.data import (
    DATE_COLUMN,
    ESTABLISHMENT_COLUMN,
    PRODUCT_COLUMN,
    TARGET_COLUMN,
    aggregate_weekly,
    regularize_weekly,
)
from pedido_predictivo.features import FEATURE_COLUMNS, build_features
from pedido_predictivo.models import baseline_predictions, cold_start_forecast


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            ESTABLISHMENT_COLUMN: [1, 1, 1, 1, 2],
            PRODUCT_COLUMN: ["A", "A", "A", "B", "A"],
            DATE_COLUMN: pd.to_datetime(
                ["2025-01-06", "2025-01-06", "2025-01-13", "2025-01-13", "2025-01-20"]
            ),
            TARGET_COLUMN: [5.0, -2.0, 4.0, 10.0, 3.0],
        }
    )


def test_aggregation_keeps_returns_and_separates_products() -> None:
    weekly = aggregate_weekly(_frame())
    row = weekly.loc[
        weekly[ESTABLISHMENT_COLUMN].eq(1)
        & weekly[PRODUCT_COLUMN].eq("A")
        & weekly[DATE_COLUMN].eq(pd.Timestamp("2025-01-06"))
    ]
    assert row[TARGET_COLUMN].item() == 3.0
    assert weekly.loc[weekly[PRODUCT_COLUMN].eq("B"), TARGET_COLUMN].item() == 10.0


def test_regularization_does_not_create_periods_before_first_observation() -> None:
    panel = regularize_weekly(aggregate_weekly(_frame()))
    product_b = panel.loc[
        panel[ESTABLISHMENT_COLUMN].eq(1) & panel[PRODUCT_COLUMN].eq("B")
    ]
    assert product_b[DATE_COLUMN].min() == pd.Timestamp("2025-01-13")


def test_features_do_not_use_current_or_future_target() -> None:
    weekly = aggregate_weekly(_frame())
    panel = regularize_weekly(weekly, include_future=True)
    original, mapping = build_features(panel)

    changed = panel.copy()
    changed.loc[changed[DATE_COLUMN].eq(pd.Timestamp("2025-01-20")), TARGET_COLUMN] = 9999
    altered, _ = build_features(changed, mapping)

    past = original[DATE_COLUMN].le(pd.Timestamp("2025-01-20"))
    pd.testing.assert_frame_equal(
        original.loc[past, FEATURE_COLUMNS].reset_index(drop=True),
        altered.loc[past, FEATURE_COLUMNS].reset_index(drop=True),
    )


def test_baselines_are_non_negative() -> None:
    frame = pd.DataFrame({"lag_1": [-3.0], "rolling_mean_4": [-1.0]})
    predictions = baseline_predictions(frame)
    assert predictions["ultima_cantidad"].item() == 0.0
    assert predictions["media_movil_4"].item() == 0.0


def test_cold_start_fallback_is_explicit() -> None:
    value, method = cold_start_forecast(pd.Series([0.0, 2.0, 4.0]))
    assert value == 3.0
    assert method == "fallback_mediana_positiva_producto"
    assert cold_start_forecast(None, None) == (0.0, "fallback_sin_historico")


def test_commercial_rounding_only_when_rule_exists() -> None:
    assert round_to_multiple(3.2, None) == 3.2
    assert round_to_multiple(3.2, 2.0) == 4.0
    with pytest.raises(ValueError):
        round_to_multiple(3.2, 0)
