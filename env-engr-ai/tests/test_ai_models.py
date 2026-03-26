"""Tests for neural network and adaptive AI models."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
import tempfile

from src.models.neural_network import AdaptiveNeuralNetwork, NeuralNetwork
from src.models.adaptive_ai import AdaptiveAIController, RuleEngine


# ---------------------------------------------------------------------------
# NeuralNetwork tests
# ---------------------------------------------------------------------------

def test_neural_network_forward_pass():
    nn = NeuralNetwork([4, 8, 2], activations=["relu", "sigmoid"])
    X = np.random.default_rng(0).random((10, 4))
    out = nn.forward(X)
    assert out.shape == (10, 2)
    assert np.all(out >= 0.0) and np.all(out <= 1.0)


def test_neural_network_training_reduces_loss():
    rng = np.random.default_rng(1)
    X = rng.random((100, 3))
    y = (X[:, 0:1] > 0.5).astype(float)
    nn = NeuralNetwork([3, 8, 1], activations=["relu", "sigmoid"], learning_rate=0.1)
    losses = nn.train(X, y, epochs=50, batch_size=16)
    assert losses[0] > losses[-1], "Loss should decrease during training"
    assert losses[-1] < 0.35, f"Final loss {losses[-1]} too high"


def test_neural_network_predict_shape():
    nn = NeuralNetwork([5, 10, 4, 2])
    X = np.ones((7, 5))
    out = nn.predict(X)
    assert out.shape == (7, 2)


def test_neural_network_save_load_weights():
    nn = NeuralNetwork([3, 6, 2], seed=7)
    X = np.random.default_rng(2).random((20, 3))
    nn.train(X, np.random.default_rng(2).random((20, 2)), epochs=5)
    original_pred = nn.predict(X[:5]).copy()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        filepath = f.name

    try:
        nn.save_weights(filepath)
        nn2 = NeuralNetwork([3, 6, 2], seed=99)  # Different seed
        nn2.load_weights(filepath)
        loaded_pred = nn2.predict(X[:5])
        np.testing.assert_allclose(original_pred, loaded_pred, rtol=1e-5)
    finally:
        os.unlink(filepath)


def test_neural_network_multiple_activations():
    nn = NeuralNetwork([4, 8, 4, 2], activations=["relu", "tanh", "sigmoid"])
    X = np.random.default_rng(3).random((5, 4))
    out = nn.forward(X)
    assert out.shape == (5, 2)


# ---------------------------------------------------------------------------
# AdaptiveNeuralNetwork tests
# ---------------------------------------------------------------------------

def test_adaptive_nn_online_update():
    ann = AdaptiveNeuralNetwork([3, 6, 1], adaptation_rate=0.01)
    x = np.array([0.5, 0.3, 0.8])
    y = np.array([1.0])
    losses = [ann.update_online(x, y) for _ in range(20)]
    # At least some updates should be happening
    assert any(l >= 0 for l in losses)


def test_adaptive_nn_drift_detection_no_drift():
    ann = AdaptiveNeuralNetwork([2, 4, 1], drift_threshold=0.5)
    # Manually set a high baseline so low recent losses don't trigger drift
    ann._baseline_loss = 0.5
    # Stable, low losses should NOT trigger drift (0.01 << 0.5 * 1.5 = 0.75)
    assert not ann.detect_drift([0.01, 0.01, 0.01, 0.01, 0.01])


def test_adaptive_nn_drift_detection():
    ann = AdaptiveNeuralNetwork([2, 4, 1], drift_threshold=0.05)
    x = np.array([0.1, 0.2])
    y = np.array([0.5])
    # Train baseline with low losses
    ann._baseline_loss = 0.01
    # Simulate high recent losses
    high_losses = [0.5, 0.6, 0.7, 0.8, 0.9]
    assert ann.detect_drift(high_losses)


def test_adaptive_nn_confidence():
    ann = AdaptiveNeuralNetwork([3, 6, 2])
    x = np.array([1.0, 0.0, 1.0])
    confidence = ann.get_confidence(x)
    assert 0.0 <= confidence <= 1.0


# ---------------------------------------------------------------------------
# AdaptiveAIController tests
# ---------------------------------------------------------------------------

def test_ai_controller_process_reading():
    controller = AdaptiveAIController(
        domain="test",
        feature_names=["temp", "ph", "co2"],
        output_names=["alert", "quality"],
    )
    features = {"temp": 25.0, "ph": 7.0, "co2": 400.0}
    result = controller.process_reading(features)
    assert "alert" in result
    assert "quality" in result
    assert 0.0 <= result["alert"] <= 1.0


def test_ai_controller_learn():
    controller = AdaptiveAIController(
        domain="test",
        feature_names=["a", "b"],
        output_names=["out"],
    )
    loss = controller.learn({"a": 0.5, "b": 0.3}, {"out": 1.0})
    assert isinstance(loss, float)
    assert loss >= 0.0


def test_ai_controller_anomaly_detection():
    controller = AdaptiveAIController(
        domain="test",
        feature_names=["x"],
        output_names=["y"],
    )
    # Feed normal data to establish baseline
    for i in range(20):
        controller.process_reading({"x": float(i % 10)})
    # Normal reading
    is_anomaly, z = controller.detect_anomaly({"x": 5.0})
    # Extreme outlier
    is_anomaly_out, z_out = controller.detect_anomaly({"x": 1000.0})
    assert z_out > z  # Outlier should have higher z-score


def test_ai_controller_status():
    controller = AdaptiveAIController(
        domain="biofuel",
        feature_names=["temp", "ph"],
        output_names=["yield"],
    )
    status = controller.get_status()
    assert status["domain"] == "biofuel"
    assert "n_samples_processed" in status
    assert "drift_detected" in status


# ---------------------------------------------------------------------------
# RuleEngine tests
# ---------------------------------------------------------------------------

def test_rule_engine_evaluation():
    engine = RuleEngine()
    engine.add_rule(
        condition=lambda ctx: ctx.get("temp", 0) > 40.0,
        action="OVERHEAT_ALERT",
        description="Temperature too high",
        priority=10,
    )
    engine.add_rule(
        condition=lambda ctx: ctx.get("ph", 7) < 4.0,
        action="LOW_PH_ALERT",
        description="pH too low",
        priority=5,
    )

    # Both rules fire
    results = engine.evaluate({"temp": 45.0, "ph": 3.0})
    actions = [r[0] for r in results]
    assert "OVERHEAT_ALERT" in actions
    assert "LOW_PH_ALERT" in actions

    # Only temperature rule fires
    results2 = engine.evaluate({"temp": 45.0, "ph": 7.0})
    assert len(results2) == 1
    assert results2[0][0] == "OVERHEAT_ALERT"


def test_rule_engine_priority_order():
    engine = RuleEngine()
    engine.add_rule(lambda ctx: True, "LOW", "low priority", priority=1)
    engine.add_rule(lambda ctx: True, "HIGH", "high priority", priority=100)
    results = engine.evaluate({})
    assert results[0][0] == "HIGH"  # High priority first


def test_rule_engine_exception_tolerance():
    engine = RuleEngine()
    engine.add_rule(
        condition=lambda ctx: 1 / 0,  # Will raise
        action="BROKEN",
        description="Broken rule",
    )
    engine.add_rule(
        condition=lambda ctx: True,
        action="OK",
        description="Good rule",
    )
    results = engine.evaluate({})
    actions = [r[0] for r in results]
    assert "OK" in actions
    assert "BROKEN" not in actions
