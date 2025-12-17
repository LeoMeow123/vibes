"""Gradient-free optimization methods."""

from typing import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize


def minimize_gradient_free(
    func: Callable[[NDArray[np.float64]], float],
    x0: NDArray[np.float64],
    method: str = "Nelder-Mead",
    bounds: list[tuple[float, float]] | None = None,
    maxiter: int = 1000,
    **kwargs,
) -> dict:
    """Minimize a function using gradient-free methods.

    Args:
        func: Objective function to minimize.
        x0: Initial guess.
        method: Optimization method. Options: 'Nelder-Mead', 'Powell', 'COBYLA'.
        bounds: Bounds for variables (only used with certain methods).
        maxiter: Maximum number of iterations.
        **kwargs: Additional arguments passed to scipy.optimize.minimize.

    Returns:
        Optimization result dictionary.
    """
    # TODO: Implement your custom gradient-free optimization wrapper here
    result = minimize(
        func,
        x0,
        method=method,
        bounds=bounds,
        options={"maxiter": maxiter},
        **kwargs,
    )
    return {
        "x": result.x,
        "fun": result.fun,
        "success": result.success,
        "nit": result.nit,
        "message": result.message,
    }
