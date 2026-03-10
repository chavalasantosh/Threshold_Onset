# Local Version Control System

Automatic file watching and version tracking.

## Architecture

```
watchfiles (file monitoring)
    ↓
content hash (hashlib)
    ↓
diff / snapshot
    ↓
local version store (sqlite + files)
```

## Features

- **Automatic tracking**: Watches files for changes
- **Content hashing**: SHA256 hashes detect actual changes
- **Diffs**: Stores unified diffs between versions
- **SQLite metadata**: Lightweight database for version history
- **File snapshots**: Stores actual file content by hash

## Usage

### Start watching

```bash
python version_control.py
```

This will:
- Watch `phase0/` and `AXIOMS.md` for changes
- Automatically create snapshots when files change
- Store metadata in `.versions.db`
- Store file content in `versions/` directory

### Query history

```python
from version_control import LocalVersionControl

vc = LocalVersionControl()
history = vc.get_history(file_path="phase0/phase0.py", limit=10)
for entry in history:
    print(entry)
```

## Database Schema

**snapshots table:**
- `id`: Snapshot ID
- `timestamp`: ISO timestamp
- `file_path`: Relative file path
- `content_hash`: SHA256 hash of content
- `snapshot_path`: Path to stored snapshot file
- `parent_hash`: Hash of previous version

**file_history table:**
- `id`: History entry ID
- `snapshot_id`: Reference to snapshot
- `file_path`: File path
- `old_hash`: Previous hash
- `new_hash`: New hash
- `diff_path`: Path to diff file
- `timestamp`: Change timestamp

## Tracked Paths

Currently tracking:
- `phase0/` (all files in phase0 directory)
- `AXIOMS.md`

To add more paths, edit `tracked_paths` in `version_control.py`.

## Storage

- **Metadata**: `.versions.db` (SQLite)
- **Snapshots**: `versions/{hash}_{filename}`
- **Diffs**: `versions/{hash}_{filename}.diff`

## No Git Required

This is completely local. No git, github, or gitlab.
