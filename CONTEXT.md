# Vibes Project Context

> **CLAUDE CODE INSTRUCTION: This file is private and should NEVER be committed or pushed to git. Do not include this file in any git add, commit, or push operations.**

## Overview
This is a "weapon base" repository for small but useful scientific tools used in publications and projects. Created by LeoMeow123 (y9li@ucsd.edu), inspired by talmolab's approach to tooling.

**GitHub Repo:** https://github.com/LeoMeow123/vibes

## Repository Structure
```
vibes/
├── src/vibing/
│   ├── optimization/      # L-BFGS-B and gradient-free methods (working)
│   ├── plotting/          # Figure setup and multi-format export (working)
│   ├── powerwell/         # Placeholder - needs implementation
│   ├── undistortion/      # Placeholder - links to external repos
│   └── sleap_convert/     # Placeholder - slp <-> yml conversion
├── tests/
│   └── test_optimization.py  # Tests pass
├── pyproject.toml         # uv/hatchling build system
└── README.md
```

## Tools Status

| Tool | Status | Notes |
|------|--------|-------|
| `optimization` | **Working** | L-BFGS-B + gradient-free (Nelder-Mead, Powell, COBYLA) wrappers |
| `plotting` | **Working** | `setup_figure()`, `save_figure()` for publication figures |
| `powerwell` | Placeholder | Needs user's notebook/script to implement |
| `undistortion` | Links only | See external repos below |
| `sleap_convert` | Placeholder | slp to yml, yml to slp - needs implementation |

## External Undistortion Repos (linked in README)
1. **[spacecage-undistort](https://github.com/talmolab/spacecage-undistort)** - NASA SpaceCage fisheye correction with ROI calibration + SLEAP coordinate transform
2. **[tmaze-undistort](https://github.com/LeoMeow123/tmaze-undistort)** - T-maze lens distortion + perspective transform to top-down views

## Planned Tools to Add
From user's initial list:
- **LMM (Gradient vs gradient-free)** - partially done in `optimization/`
- **L-BFGS-B** - done in `optimization/lbfgsb.py`
- **Powerwell** - placeholder ready, needs user's code
- **Plotting** - basic implementation done, can be extended
- **Undistortion** - external repos linked
- **Multiple slp to yml, yml to slp** - placeholder ready, needs user's code

## Important Rules
- **NEVER modify anything in talmolab repos** - only modify LeoMeow123 repos
- All tools should use `uv` for package management
- User will feed notebooks/scripts to convert into proper modules

## Development Commands
```bash
cd /root/vast/leo/vibing
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -v
ruff check src/
```

## Git Info
- Remote: https://github.com/LeoMeow123/vibes.git
- Branch: main
- User: LeoMeow123 <y9li@ucsd.edu>

## Next Steps
1. User will provide notebooks/scripts for:
   - Powerwell analysis
   - SLEAP conversion (slp <-> yml)
   - Any additional plotting utilities
   - Any optimization enhancements
2. Convert those into proper modules in this repo
3. Add tests for new modules
