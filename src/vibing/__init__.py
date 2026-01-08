"""Vibing: Small but useful tools for scientific publications and projects."""

__version__ = "0.2.0"

# Core modules (always available)
from vibing import (
    optimization,
    plotting,
    powerwell,
)

__all__ = [
    "__version__",
    "optimization",
    "plotting",
    "powerwell",
]

# Optional modules - only import if dependencies are available
try:
    from vibing import calibration
    __all__.append("calibration")
except ImportError:
    pass

try:
    from vibing import geometry
    __all__.append("geometry")
except ImportError:
    pass

try:
    from vibing import pose
    __all__.append("pose")
except ImportError:
    pass

try:
    from vibing import sleap_convert
    __all__.append("sleap_convert")
except ImportError:
    pass

try:
    from vibing import undistortion
    __all__.append("undistortion")
except ImportError:
    pass
