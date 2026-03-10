# Phase 6: Meaning Discovery

**Enterprise Implementation - ✅ COMPLETE**

## Purpose

Discover meaning clusters from consequence vectors using k-medoids clustering.

## Core Principle

**Meaning = Clusters in Consequence Space**

Identities with similar consequence patterns form meaning clusters.

## Key Components (All Corrections Applied)

1. **Vector Normalization**: Normalize vectors to [0, 1] range
2. **k-Medoids Clustering**: PAM algorithm (deterministic)
3. **Stability-Based Selection**: Auto-select optimal k (CORRECTED)
4. **Meaning Signature Extraction**: Cluster centroids (denormalized)

## Implementation Status

✅ **IMPLEMENTED**

All corrections applied:
- ✅ Stability-based cluster selection (not hand-chosen)
- ✅ Deterministic k-medoids (PAM algorithm)
- ✅ Meaning signature extraction
- ✅ No hidden imports

## Files

- `meaning_discovery.py` - Main engine (✅ Complete)
- `clustering.py` - k-medoids clustering (✅ Complete)
- `normalization.py` - Vector normalization (✅ Complete)

## Usage

```python
from threshold_onset.semantic.phase6 import MeaningDiscoveryEngine
from threshold_onset.semantic.phase5 import ConsequenceFieldEngine

# Build consequence field (Phase 5)
consequence_field = consequence_engine.build()

# Discover meaning
meaning_engine = MeaningDiscoveryEngine(consequence_field)
meaning_map = meaning_engine.discover(seed=42)

# Get cluster for identity
cluster_id = meaning_engine.get_cluster(identity_hash)

# Get signature
signature = meaning_engine.get_signature(cluster_id)
print(f"Cluster size: {signature.size}")
print(f"Centroid: {signature.centroid}")

# Save
meaning_engine.save('meaning_map.json')
```

## Dependencies

- Phase 5: Consequence Field (required)

## Output

`meaning_map.json` with:
- Clusters: Dictionary of cluster_id -> MeaningSignature
  - `centroid`: Denormalized centroid vector
  - `size`: Number of identities in cluster
  - `identities`: List of identity hashes
- Identity-to-cluster mapping
- Metadata: num_clusters, normalization ranges, etc.

## Algorithm

1. **Normalize**: Convert consequence vectors to [0, 1] range
2. **Select k**: Stability-based selection (if not specified)
3. **Cluster**: k-medoids PAM algorithm
4. **Extract**: Compute cluster centroids (denormalized)

## Testing

See `tests/test_phase6.py` (to be implemented)

---

**See CORRECTIONS_APPLIED.md for stability-based selection details.**
