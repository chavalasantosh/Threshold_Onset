# Tools (`src/tools/`)

This directory contains utility tools for the THRESHOLD_ONSET project.

## Contents

### Version Control System
- `version_control.py` - Local version control implementation
  - File watching with `watchfiles`
  - Content hashing with SHA256
  - SQLite metadata storage
  - Unified diffs between versions

- `watch_version.py` - Watcher script to start version control

## Purpose

These tools provide **local version control** (no Git/GitHub/GitLab) for:
- Tracking changes to source code
- Creating version snapshots
- Generating diffs between versions
- Maintaining project history

## Usage

### Start Version Control Watcher

```bash
python src/tools/watch_version.py
```

Or from main entry point:

```bash
python main.py watch
```

## What It Tracks

Automatically tracks changes to:
- `src/` - All source code
- `docs/` - All documentation
- `README.md` - Root README

## Version Storage

Versions are stored in:
- `versions/` - Version snapshots directory
- `.versions.db` - SQLite database with metadata

## Dependencies

- `watchfiles` - File system watching (only third-party dependency allowed)

## Documentation

See `docs/` subdirectory for detailed version control documentation.
