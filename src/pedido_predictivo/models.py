"""Referencias y modelos globales para CantidadUMB."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from .features import FEATURE_COLUMNS

MAX_TRAIN_ROWS = 500_000


def _sample_training(frame: pd.DataFrame, max_rows: int = MAX_TRAIN_ROWS) -> pd.DataFrame:
    if len(frame) <= max_rows:
        return frame
    return frame.sample(max_rows, random_state=42).sort_index()


def baseline_predictions(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    """Predicciones de referencia, siempre no negativas."""
    return {
        "ultima_cantidad": frame["lag_1"].clip(lower=0).to_numpy(),
        "media_movil_4": frame["rolling_mean_4"].clip(lower=0).to_numpy(),
    }


@dataclass
class DirectQuantityModel:
    """Regresión global directa; la salida se restringe a compras no negativas."""

    estimator: HistGradientBoostingRegressor | None = None

    def fit(self, frame: pd.DataFrame, target: str) -> "DirectQuantityModel":
        train = _sample_training(frame)
        self.estimator = HistGradientBoostingRegressor(
            loss="squared_error",
            learning_rate=0.08,
            max_iter=120,
            max_leaf_nodes=31,
            min_samples_leaf=40,
            l2_regularization=1.0,
            categorical_features=["product_code"],
            random_state=42,
        )
        self.estimator.fit(train[FEATURE_COLUMNS], train[target])
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        if self.estimator is None:
            raise RuntimeError("El modelo no está entrenado")
        return np.clip(self.estimator.predict(frame[FEATURE_COLUMNS]), 0.0, None)


@dataclass
class TwoStageQuantityModel:
    """Probabilidad de compra multiplicada por cantidad condicionada positiva."""

    classifier: HistGradientBoostingClassifier | None = None
    regressor: HistGradientBoostingRegressor | None = None

    def fit(self, frame: pd.DataFrame, target: str) -> "TwoStageQuantityModel":
        train = _sample_training(frame)
        purchase = train[target].gt(0)
        self.classifier = HistGradientBoostingClassifier(
            loss="log_loss",
            learning_rate=0.08,
            max_iter=90,
            max_leaf_nodes=31,
            min_samples_leaf=40,
            l2_regularization=1.0,
            categorical_features=["product_code"],
            random_state=42,
        )
        self.classifier.fit(train[FEATURE_COLUMNS], purchase)

        positive = train.loc[purchase]
        self.regressor = HistGradientBoostingRegressor(
            loss="poisson",
            learning_rate=0.08,
            max_iter=100,
            max_leaf_nodes=31,
            min_samples_leaf=30,
            l2_regularization=1.0,
            categorical_features=["product_code"],
            random_state=42,
        )
        self.regressor.fit(positive[FEATURE_COLUMNS], positive[target])
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        if self.classifier is None or self.regressor is None:
            raise RuntimeError("El modelo no está entrenado")
        probability = self.classifier.predict_proba(frame[FEATURE_COLUMNS])[:, 1]
        amount = np.clip(self.regressor.predict(frame[FEATURE_COLUMNS]), 0.0, None)
        return probability * amount


def cold_start_forecast(
    product_history: pd.Series | None,
    establishment_history: pd.Series | None = None,
) -> tuple[float, str]:
    """Alternativa conservadora para entidades nuevas."""
    if product_history is not None and len(product_history):
        positive = product_history[product_history > 0]
        if len(positive):
            return float(positive.median()), "fallback_mediana_positiva_producto"
    if establishment_history is not None and len(establishment_history):
        positive = establishment_history[establishment_history > 0]
        if len(positive):
            return float(positive.median()), "fallback_mediana_positiva_establecimiento"
    return 0.0, "fallback_sin_historico"
