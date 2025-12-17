# vibing

A collection of small but useful tools for scientific publications and projects.

## Installation

```bash
# Using uv (recommended)
uv pip install vibing

# From source
git clone https://github.com/LeoMeow123/vibing.git
cd vibing
uv pip install -e .

# With optional dependencies
uv pip install -e ".[sleap]"  # SLEAP conversion tools
uv pip install -e ".[dev]"   # Development tools
uv pip install -e ".[all]"   # Everything
```

## Tools

### Optimization (`vibing.optimization`)
Gradient-based and gradient-free optimization wrappers.
- `minimize_lbfgsb` - L-BFGS-B optimization
- `minimize_gradient_free` - Gradient-free methods (Nelder-Mead, Powell, COBYLA)

### Plotting (`vibing.plotting`)
Utilities for creating publication-quality figures.
- `setup_figure` - Set up figures with consistent styling
- `save_figure` - Save figures in multiple formats

### Powerwell (`vibing.powerwell`)
Powerwell analysis tools.
- *Coming soon*

### Undistortion (`vibing.undistortion`)
Image undistortion utilities.
- *Coming soon*

### SLEAP Convert (`vibing.sleap_convert`)
Convert between SLEAP file formats.
- slp to yml conversion
- yml to slp conversion
- *Coming soon*

## Quick Start

```python
import numpy as np
from vibing.optimization import minimize_lbfgsb
from vibing.plotting import setup_figure, save_figure

# Optimization example
def objective(x):
    return (x[0] - 1) ** 2 + (x[1] - 2) ** 2

result = minimize_lbfgsb(objective, np.array([0.0, 0.0]))
print(f"Optimal x: {result['x']}")

# Plotting example
fig, ax = setup_figure(width=6, height=4)
ax.plot([1, 2, 3], [1, 4, 9])
save_figure(fig, "my_plot", formats=["png", "pdf"])
```

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/LeoMeow123/vibing.git
cd vibing
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
```

## License

MIT License
