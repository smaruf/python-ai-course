"""
High-level adaptive AI controller and rule engine.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

import numpy as np

from src.models.neural_network import AdaptiveNeuralNetwork


class AdaptiveAIController:
    """
    High-level adaptive AI controller that wraps AdaptiveNeuralNetwork.
    Handles online learning, anomaly detection, and model management.
    """

    def __init__(
        self,
        domain: str,
        feature_names: list[str],
        output_names: list[str],
        hidden_sizes: list[int] = None,
        learning_rate: float = 0.01,
        adaptation_rate: float = 0.001,
    ) -> None:
        self.domain = domain
        self.feature_names = feature_names
        self.output_names = output_names

        n_in = len(feature_names)
        n_out = len(output_names)
        hidden = hidden_sizes or [max(8, n_in * 2), max(8, n_in)]
        layer_sizes = [n_in] + hidden + [n_out]
        activations = ["relu"] * len(hidden) + ["sigmoid"]

        self._model = AdaptiveNeuralNetwork(
            layer_sizes=layer_sizes,
            activations=activations,
            learning_rate=learning_rate,
            adaptation_rate=adaptation_rate,
        )

        # Statistics for anomaly detection (online mean/var)
        self._feature_means = np.zeros(n_in)
        self._feature_vars = np.ones(n_in)
        self._n_samples = 0
        self._recent_losses: list[float] = []

    def _features_to_array(self, features: dict[str, float]) -> np.ndarray:
        return np.array([features.get(name, 0.0) for name in self.feature_names],
                        dtype=float)

    def _normalize(self, x: np.ndarray) -> np.ndarray:
        std = np.sqrt(self._feature_vars + 1e-8)
        return (x - self._feature_means) / std

    def _update_stats(self, x: np.ndarray) -> None:
        """Welford's online algorithm for mean and variance."""
        self._n_samples += 1
        delta = x - self._feature_means
        self._feature_means += delta / self._n_samples
        delta2 = x - self._feature_means
        self._feature_vars += (delta * delta2 - self._feature_vars) / self._n_samples

    def process_reading(self, features: dict[str, float]) -> dict[str, float]:
        """Process a sensor reading, return predictions."""
        x = self._features_to_array(features)
        self._update_stats(x)
        x_norm = self._normalize(x)
        out = self._model.predict(x_norm.reshape(1, -1)).flatten()
        return {name: float(val) for name, val in zip(self.output_names, out)}

    def learn(self, features: dict[str, float], labels: dict[str, float]) -> float:
        """Online learning from labeled data. Returns current loss."""
        x = self._features_to_array(features)
        self._update_stats(x)
        x_norm = self._normalize(x)
        y = np.array([labels.get(name, 0.0) for name in self.output_names], dtype=float)
        loss = self._model.update_online(x_norm, y)
        self._recent_losses.append(loss)
        if len(self._recent_losses) > 50:
            self._recent_losses.pop(0)
        return loss

    def detect_anomaly(
        self, features: dict[str, float], threshold: float = 3.0
    ) -> tuple[bool, float]:
        """
        Statistical anomaly detection using z-score.
        Returns (is_anomaly, max_z_score).
        """
        x = self._features_to_array(features)
        std = np.sqrt(self._feature_vars + 1e-8)
        z_scores = np.abs((x - self._feature_means) / std)
        max_z = float(np.max(z_scores))
        return max_z > threshold, max_z

    def get_status(self) -> dict[str, Any]:
        drift = self._model.detect_drift(self._recent_losses)
        return {
            "domain": self.domain,
            "n_samples_processed": self._n_samples,
            "recent_loss_mean": float(np.mean(self._recent_losses[-10:])) if self._recent_losses else 0.0,
            "drift_detected": drift,
            "model_architecture": self._model.layer_sizes,
        }


class RuleEngine:
    """Priority-ordered rule evaluator for domain-specific decisions."""

    def __init__(self) -> None:
        # (priority, condition, action, description)
        self._rules: list[tuple[int, Callable, str, str]] = []

    def add_rule(
        self,
        condition: Callable,
        action: str,
        description: str,
        priority: int = 0,
    ) -> None:
        self._rules.append((priority, condition, action, description))
        # Keep sorted by priority descending (higher priority first)
        self._rules.sort(key=lambda r: r[0], reverse=True)

    def evaluate(self, context: dict[str, Any]) -> list[tuple[str, str]]:
        """Return list of (action, description) for all matching rules."""
        results: list[tuple[str, str]] = []
        for _priority, condition, action, description in self._rules:
            try:
                if condition(context):
                    results.append((action, description))
            except Exception:
                pass
        return results
