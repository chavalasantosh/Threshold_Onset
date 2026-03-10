# Version Snapshots (`versions/`)

This directory contains automatic version snapshots created by the local version control system.

## Purpose

The version control system automatically creates snapshots of:
- Source code (`src/`)
- Documentation (`docs/`)
- Root files (`README.md`, etc.)

## Structure

```
versions/
└── v0.1.0_YYYYMMDD_HHMMSS/
    ├── src/           # Snapshot of source code
    ├── docs/          # Snapshot of documentation
    └── [other files]  # Snapshot of tracked files
```

## How It Works

1. File watcher detects changes
2. Content is hashed (SHA256)
3. If changed, snapshot is created
4. Metadata stored in `.versions.db`

## Usage

Versions are created automatically. To view:
- Check `versions/` directory
- Query `.versions.db` for metadata
- Use version control tools for diffs

## Metadata

Version metadata stored in `.versions.db`:
- Version ID
- Timestamp
- File paths
- Content hashes
- Change descriptions

## Related Documentation

- Version control: `src/tools/docs/VERSION_CONTROL.md`
- Tools: `src/tools/README.md`
