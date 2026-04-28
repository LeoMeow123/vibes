# SLEAP Skill for Claude Code

A Claude Code skill that gives Claude expert knowledge about SLEAP pose estimation files (`.slp`, `.h5`, `.pkg.slp`) and the `sleap-io` Python API. When active, Claude knows exactly how to load, inspect, manipulate, and extract data from SLEAP files without guessing or hallucinating API calls.

## Why This Exists

SLEAP's Python API (`sleap-io`) has several non-obvious patterns and pitfalls:

- `Points` are structured numpy arrays, not Point objects — access with `pts[i]['score']`, not `pts[i].score`
- `video.filename` stores the ORIGINAL path from training time, which is often stale after files are moved
- `len(labels)` returns labeled frames, not total video frames
- The `Labels` constructor takes `skeletons=` (plural list), not `skeleton=`
- `sleap-io` (lightweight I/O) vs `sleap` (full package with GUI/training) are different packages

Without the skill, Claude often gets these wrong. With it, Claude has a reliable reference for the sleap-io 0.5.x API and writes correct code on the first try.

## What's in the Skill

| Section | Content |
|---------|---------|
| **Quick Start** | `sio.load_file()` one-liner |
| **Core Objects** | `Labels`, `Skeleton`, `Video`, `LabeledFrame`, `Instance`, `Points` — all attributes and access patterns |
| **Common Patterns** | Build trajectory array (T x J x 2), pick best instance, per-keypoint confidence, node indexing, FPS extraction |
| **Known Pitfalls** | 7 documented gotchas with correct/incorrect code examples |
| **File Formats** | `.slp`, `.pkg.slp`, `.analysis.h5`, `.predictions.slp` — what each is and when to use it |
| **Environment** | Package name, install command, version info |

## Installation

### 1. Copy the skill folder

The skill is a single Markdown file at `~/.claude/skills/sleap/SKILL.md`. Copy it to the same path on any workstation:

```bash
# From a machine that already has it (e.g., exx)
mkdir -p ~/.claude/skills/sleap
cp /home/exx/vast/leo/vibing/sleap-skill/SKILL.md ~/.claude/skills/sleap/SKILL.md
```

Or if you have VAST access:

```bash
mkdir -p ~/.claude/skills/sleap
cp /home/exx/vast/leo/vibing/sleap-skill/SKILL.md ~/.claude/skills/sleap/SKILL.md
```

Or from any machine with this repo cloned:

```bash
mkdir -p ~/.claude/skills/sleap
cp <repo>/sleap-skill/SKILL.md ~/.claude/skills/sleap/SKILL.md
```

### 2. Verify

Start a new Claude Code session and type:

```
/sleap load a .slp file and print the skeleton nodes
```

Claude should respond with correct `sleap-io` code using `sio.load_file()` and `[n.name for n in labels.skeleton.nodes]`.

### 3. Prerequisites

The skill tells Claude *how* to write sleap-io code — you still need the package installed in your Python environment:

```bash
pip install sleap-io
# or
uv pip install sleap-io
```

Current tested version: `sleap-io 0.5.8`

## Usage

The skill activates automatically when Claude detects SLEAP-related work. You can also invoke it directly:

```
/sleap extract keypoint coordinates from predictions.slp as a numpy array
/sleap check which frames have NaN keypoints
/sleap build a trajectory array from a multi-animal .slp file
```

## How Claude Code Skills Work

Skills are Markdown files in `~/.claude/skills/<name>/SKILL.md` with a YAML frontmatter header:

```yaml
---
name: sleap
description: >
  Reference for working with SLEAP pose estimation files...
user-invocable: true
argument-hint: "[task description]"
---
```

- **`name`**: Skill identifier (used as `/sleap` command)
- **`description`**: Tells Claude when to auto-activate the skill
- **`user-invocable: true`**: Enables the `/sleap` slash command
- **`argument-hint`**: Shows usage hint in the skill list

The rest of the file is the knowledge that gets injected into Claude's context when the skill activates. No config changes or restarts needed — just drop the file and start a new session.

## File Structure

```
sleap-skill/
  README.md       # This file (how to install and use)
  SKILL.md        # The actual skill file (copy to ~/.claude/skills/sleap/)
```
