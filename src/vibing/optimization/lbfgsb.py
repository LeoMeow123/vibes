"""L-BFGS-B optimization wrapper."""

from typing import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize


def minimize_lbfgsb(
    func: Callable[[NDArray[np.float64]], float],
    x0: NDArray[np.float64],
    bounds: list[tuple[float, float]] | None = None,
    maxiter: int = 1000,
    **kwargs,
) -> dict:
    """Minimize a function using L-BFGS-B algorithm.

    Args:
        func: Objective function to minimize.
        x0: Initial guess.
        bounds: Bounds for variables as list of (min, max) tuples.
        maxiter: Maximum number of iterations.
        **kwargs: Additional arguments passed to scipy.optimize.minimize.

    Returns:
        Optimization result dictionary.
    """
    # TODO: Implement your custom L-BFGS-B wrapper here
    result = minimize(
        func,
        x0,
        method="L-BFGS-B",
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
