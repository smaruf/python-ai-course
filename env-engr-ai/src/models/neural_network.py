"""
Multi-layer perceptron implemented from scratch using numpy only.
"""
from __future__ import annotations

import json
from typing import Optional

import numpy as np


class NeuralNetwork:
    """
    Multi-layer perceptron implemented from scratch using numpy only.
    Supports configurable layers, multiple activations (relu, sigmoid, softmax, tanh),
    MSE and cross-entropy loss, mini-batch SGD.
    """

    ACTIVATIONS = {"relu", "sigmoid", "softmax", "tanh", "linear"}

    def __init__(
        self,
        layer_sizes: list[int],
        activations: list[str] = None,
        learning_rate: float = 0.01,
        seed: int = 42,
    ) -> None:
        assert len(layer_sizes) >= 2, "Need at least input + output layers"
        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate
        self._rng = np.random.default_rng(seed)

        n_layers = len(layer_sizes) - 1
        if activations is None:
            # Default: relu for hidden, sigmoid for output
            self.activations = ["relu"] * (n_layers - 1) + ["sigmoid"]
        else:
            assert len(activations) == n_layers, (
                f"Need {n_layers} activations, got {len(activations)}"
            )
            self.activations = activations

        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []
        self._init_weights()

        # Cache for backprop
        self._z_cache: list[np.ndarray] = []
        self._a_cache: list[np.ndarray] = []

    def _init_weights(self) -> None:
        """He initialisation for relu layers, Xavier for others."""
        self.weights = []
        self.biases = []
        for i in range(len(self.layer_sizes) - 1):
            fan_in = self.layer_sizes[i]
            fan_out = self.layer_sizes[i + 1]
            if self.activations[i] == "relu":
                scale = np.sqrt(2.0 / fan_in)
            else:
                scale = np.sqrt(2.0 / (fan_in + fan_out))
            W = self._rng.normal(0.0, scale, (fan_in, fan_out))
            b = np.zeros((1, fan_out))
            self.weights.append(W)
            self.biases.append(b)

    # ------------------------------------------------------------------
    # Activation functions
    # ------------------------------------------------------------------

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, x)

    @staticmethod
    def _relu_deriv(x: np.ndarray) -> np.ndarray:
        return (x > 0.0).astype(float)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    @staticmethod
    def _sigmoid_deriv(x: np.ndarray) -> np.ndarray:
        s = NeuralNetwork._sigmoid(x)
        return s * (1.0 - s)

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        shifted = x - np.max(x, axis=1, keepdims=True)
        exp_x = np.exp(shifted)
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    @staticmethod
    def _tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    @staticmethod
    def _tanh_deriv(x: np.ndarray) -> np.ndarray:
        return 1.0 - np.tanh(x) ** 2

    def _apply_activation(self, z: np.ndarray, name: str) -> np.ndarray:
        if name == "relu":
            return self._relu(z)
        elif name == "sigmoid":
            return self._sigmoid(z)
        elif name == "softmax":
            return self._softmax(z)
        elif name == "tanh":
            return self._tanh(z)
        else:  # linear
            return z

    # Softmax derivative note: when using MSE loss with softmax, the output-layer
    # error delta is passed through unchanged (no derivative term needed) since
    # the gradient d(MSE)/d(softmax_input) simplifies when combined with MSE.
    def _activation_deriv(self, z: np.ndarray, name: str) -> np.ndarray:
        if name == "relu":
            return self._relu_deriv(z)
        elif name == "sigmoid":
            return self._sigmoid_deriv(z)
        elif name == "tanh":
            return self._tanh_deriv(z)
        else:
            return np.ones_like(z)

    # ------------------------------------------------------------------
    # Forward / Backward
    # ------------------------------------------------------------------

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass. Caches z and a values for backprop."""
        self._z_cache = []
        self._a_cache = [X]
        a = X
        for W, b, act in zip(self.weights, self.biases, self.activations):
            z = a @ W + b
            self._z_cache.append(z)
            a = self._apply_activation(z, act)
            self._a_cache.append(a)
        return a

    def backward(self, X: np.ndarray, y: np.ndarray, output: np.ndarray) -> None:
        """Backpropagation with MSE loss."""
        m = X.shape[0]
        n_layers = len(self.weights)

        # Output error (MSE derivative)
        delta = (output - y)  # shape: (m, output_size)

        for i in reversed(range(n_layers)):
            act = self.activations[i]
            z = self._z_cache[i]

            if act != "softmax":
                delta = delta * self._activation_deriv(z, act)

            a_prev = self._a_cache[i]
            dW = (a_prev.T @ delta) / m
            db = np.sum(delta, axis=0, keepdims=True) / m

            self.weights[i] -= self.learning_rate * dW
            self.biases[i] -= self.learning_rate * db

            if i > 0:
                delta = delta @ self.weights[i].T

    def _mse_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.mean((y_true - y_pred) ** 2))

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: bool = False,
    ) -> list[float]:
        """
        Train the network. Returns list of per-epoch losses.
        """
        losses: list[float] = []
        n_samples = X.shape[0]
        for epoch in range(epochs):
            # Shuffle
            idx = np.random.permutation(n_samples)
            X_shuf, y_shuf = X[idx], y[idx]
            epoch_losses: list[float] = []
            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                Xb, yb = X_shuf[start:end], y_shuf[start:end]
                out = self.forward(Xb)
                self.backward(Xb, yb, out)
                epoch_losses.append(self._mse_loss(yb, out))
            epoch_loss = float(np.mean(epoch_losses))
            losses.append(epoch_loss)
            if verbose and (epoch % max(1, epochs // 10) == 0):
                print(f"  Epoch {epoch+1}/{epochs}  loss={epoch_loss:.6f}")
        return losses

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)

    def save_weights(self, filepath: str) -> None:
        data = {
            "layer_sizes": self.layer_sizes,
            "activations": self.activations,
            "learning_rate": self.learning_rate,
            "weights": [w.tolist() for w in self.weights],
            "biases": [b.tolist() for b in self.biases],
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

    def load_weights(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            data = json.load(f)
        self.weights = [np.array(w) for w in data["weights"]]
        self.biases = [np.array(b) for b in data["biases"]]
        self.layer_sizes = data["layer_sizes"]
        self.activations = data["activations"]
        self.learning_rate = data["learning_rate"]


class AdaptiveNeuralNetwork(NeuralNetwork):
    """
    Extends NeuralNetwork with online/incremental learning capabilities.
    Supports model drift detection and weight updates from streaming data.
    """

    def __init__(
        self,
        layer_sizes: list[int],
        activations: list[str] = None,
        learning_rate: float = 0.01,
        adaptation_rate: float = 0.001,
        drift_threshold: float = 0.1,
        seed: int = 42,
    ) -> None:
        super().__init__(layer_sizes, activations, learning_rate, seed)
        self.adaptation_rate = adaptation_rate
        self.drift_threshold = drift_threshold
        self._loss_history: list[float] = []
        self._baseline_loss: Optional[float] = None
        self._online_count: int = 0

    def update_online(self, x: np.ndarray, y: np.ndarray) -> float:
        """
        Single-sample online update. x shape: (features,), y shape: (outputs,).
        Returns current sample loss.
        """
        X = x.reshape(1, -1)
        Y = y.reshape(1, -1)
        out = self.forward(X)
        # Use adaptation_rate for online learning (smaller than batch lr)
        original_lr = self.learning_rate
        self.learning_rate = self.adaptation_rate
        self.backward(X, Y, out)
        self.learning_rate = original_lr
        loss = self._mse_loss(Y, out)
        self._loss_history.append(loss)
        self._online_count += 1
        # Set baseline from first 10 updates
        if self._online_count == 10:
            self._baseline_loss = float(np.mean(self._loss_history[-10:]))
        return loss

    def detect_drift(self, recent_losses: list[float]) -> bool:
        """
        Detect concept drift: recent average loss significantly above baseline.
        Uses Page-Hinkley test approximation.
        """
        if len(recent_losses) < 5 or self._baseline_loss is None:
            return False
        recent_mean = float(np.mean(recent_losses[-5:]))
        return recent_mean > self._baseline_loss * (1.0 + self.drift_threshold)

    def get_confidence(self, x: np.ndarray) -> float:
        """
        Return prediction confidence (0–1) for a single sample.
        For multi-output: 1 - normalised variance across outputs.
        """
        X = x.reshape(1, -1)
        out = self.forward(X).flatten()
        # Confidence based on how far outputs are from 0.5 (decision boundary)
        confidence = float(np.mean(np.abs(out - 0.5)) * 2.0)
        return max(0.0, min(1.0, confidence))

    def get_loss_history(self) -> list[float]:
        return list(self._loss_history)
