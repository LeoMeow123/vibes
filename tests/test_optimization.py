"""Tests for optimization module."""

import numpy as np

from vibing.optimization import minimize_lbfgsb, minimize_gradient_free


def test_minimize_lbfgsb():
    """Test L-BFGS-B optimization on simple quadratic."""

    def quadratic(x):
        return (x[0] - 1) ** 2 + (x[1] - 2) ** 2

    x0 = np.array([0.0, 0.0])
    result = minimize_lbfgsb(quadratic, x0)

    assert result["success"]
    np.testing.assert_allclose(result["x"], [1.0, 2.0], atol=1e-5)


def test_minimize_gradient_free():
    """Test gradient-free optimization on simple quadratic."""

    def quadratic(x):
        return (x[0] - 1) ** 2 + (x[1] - 2) ** 2

    x0 = np.array([0.0, 0.0])
    result = minimize_gradient_free(quadratic, x0, method="Nelder-Mead")

    assert result["success"]
    np.testing.assert_allclose(result["x"], [1.0, 2.0], atol=1e-3)
