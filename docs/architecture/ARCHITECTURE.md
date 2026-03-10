# THRESHOLD_ONSET — Architecture

## Project Structure

```
THRESHOLD_ONSET/
│
├── README.md                 # Project overview (root level only)
├── requirements.txt          # Python dependencies
├── .gitignore                # Ignore patterns
│
├── 📋 docs/                  # All documentation
│   ├── ARCHITECTURE.md        # This file - system architecture
│   ├── AXIOMS.md              # Non-negotiable design constraints
│   ├── VERSION_CONTROL.md     # Version control system docs
│   ├── PROJECT_STRUCTURE.md   # Structure reference
│   └── reference/             # Historical documents
│       ├── chatgpt.txt        # Historical conversation log
│       └── process.txt        # Process notes
│
├── 🔧 phase0/                # Phase 0: THRESHOLD_ONSET
│   ├── phase0.py              # Raw pipeline (action → trace → repeat)
│   ├── action.py              # Constraint reminder (not execution)
│   ├── trace.py               # Constraint reminder (not execution)
│   └── repetition.py          # Constraint reminder (not execution)
│
├── 🔄 tools/                  # Version control tools
│   ├── version_control.py     # Local version control system
│   └── watch_version.py       # Watcher entry point
│
└── 📚 versions/               # Version snapshots (auto-generated)
    ├── .versions.db           # SQLite metadata
    └── {hash}_{filename}      # Snapshot files
```

## Architecture Layers

### Layer 0: Axioms (Non-Negotiable)
**File:** `docs/AXIOMS.md`

- कार्य (kārya) happens before ज्ञान (jñāna)
- Function stabilizes before knowledge appears
- Design constraint, not philosophy

### Layer 1: Phase 0 Implementation
**Directory:** `phase0/`

**Allowed:**
- action, interaction, trace, repetition, persistence, stabilization

**NOT Allowed:**
- symbols, letters, meaning, tokens, embeddings, plots, coordinates

**Key File:** `phase0/phase0.py`
- Single raw pipeline
- No premature structure
- Action → trace → repeat

### Layer 2: Version Control
**Files:** `version_control.py`, `watch_version.py`

**Architecture:**
```
watchfiles (file monitoring)
    ↓
content hash (hashlib)
    ↓
diff / snapshot
    ↓
local version store (sqlite + files)
```

**Features:**
- Automatic file watching
- SHA256 content hashing
- Unified diffs
- SQLite metadata
- Local storage only (no git/github/gitlab)

## Design Principles

### 1. Phase 0 Constraints
- Code must feel raw, procedural, almost uncomfortable
- If it feels "clean", it's probably too late-stage
- Discomfort is a good sign — means we're not faking structure

### 2. Organization
- Clear separation of concerns
- Documentation at root level
- Implementation in phase-specific directories
- Version control separate from core logic

### 3. Version Control
- Automatic tracking (no manual backups)
- Hash-based change detection
- Local storage only
- Queryable history via SQLite

### 4. Maintainability
- Single responsibility per file
- Clear naming conventions
- Comprehensive documentation
- Structured directory layout

## File Responsibilities

| File | Purpose | Layer |
|------|---------|-------|
| `AXIOMS.md` | Design constraints | Layer 0 |
| `phase0/phase0.py` | Raw pipeline execution | Layer 1 |
| `phase0/action.py` | Constraint documentation | Layer 1 |
| `phase0/trace.py` | Constraint documentation | Layer 1 |
| `phase0/repetition.py` | Constraint documentation | Layer 1 |
| `tools/version_control.py` | Version control system | Layer 2 |
| `tools/watch_version.py` | Watcher entry point | Layer 2 |

## Dependencies

**External:**
- `watchfiles>=0.21.0` - File system monitoring

**Standard Library:**
- `hashlib` - Content hashing
- `sqlite3` - Metadata storage
- `difflib` - Diff computation
- `pathlib` - Path handling
- `datetime` - Timestamping

## Data Flow

### Version Control Flow
```
File Change Event
    ↓
Compute SHA256 Hash
    ↓
Compare with Last Hash
    ↓
If Changed:
    Store Snapshot → versions/
    Compute Diff → versions/
    Update Metadata → .versions.db
```

### Phase 0 Execution Flow
```
Actions (callable)
    ↓
Execute → Generate Traces
    ↓
Repeat → Collect Traces
    ↓
Return Raw Traces (no interpretation)
```

## Extension Points

### Adding New Phases
1. Create new directory: `phase1/`, `phase2/`, etc.
2. Follow same structure as `phase0/`
3. Update `AXIOMS.md` with phase-specific constraints
4. Add to version control tracked paths

### Extending Version Control
1. Modify `tracked_paths` in `version_control.py`
2. Add new tables to SQLite schema if needed
3. Extend `LocalVersionControl` class methods

## Maintenance Guidelines

1. **Keep structure clean:** Follow directory organization
2. **Document changes:** Update relevant docs when modifying
3. **Respect constraints:** Never violate Phase 0 axioms
4. **Version everything:** All code changes tracked automatically
5. **Single responsibility:** Each file has one clear purpose

## Future Architecture Considerations

- Phase 1: Structure emergence (when Phase 0 stabilizes)
- Phase 2: Identity and symbols (when structure exists)
- Phase 3+: Higher-level abstractions

**Current focus:** Phase 0 only. No premature optimization.
