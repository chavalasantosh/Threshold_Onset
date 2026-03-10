# Semantic Discovery Module - API Contracts

**Enterprise API Contract Specification**

## Contract Principles

1. **Type Safety**: All inputs/outputs are type-annotated
2. **Validation**: All inputs are validated
3. **Error Handling**: Clear error conditions
4. **Documentation**: Complete API documentation
5. **Backward Compatibility**: Changes are versioned

---

## Phase 5: Consequence Field Engine

### ConsequenceFieldEngine

**Constructor**:
```python
def __init__(
    self,
    phase2_identities: Dict[str, Any],
    phase3_relations: Dict[str, Any],
    phase4_symbols: Dict[str, Any],
    continuation_observer: Optional[ContinuationObserver] = None,
    config: Optional[Dict[str, Any]] = None
) -> None
```

**Parameters**:
- `phase2_identities`: Phase 2 identity metrics (required)
- `phase3_relations`: Phase 3 relation metrics (required)
- `phase4_symbols`: Phase 4 symbol mappings (required)
- `continuation_observer`: Optional observer instance
- `config`: Optional configuration overrides

**Raises**:
- `TypeError`: If inputs are wrong type
- `ValueError`: If inputs are invalid
- `ConsequenceFieldError`: If computation fails

**Methods**:

#### `build(k: int = 5, num_rollouts: int = 100) -> ConsequenceField`

Builds complete consequence field.

**Parameters**:
- `k`: k-step reachability horizon (default: 5)
- `num_rollouts`: Number of rollouts per identity (default: 100)

**Returns**: `ConsequenceField` object

**Raises**:
- `ConsequenceFieldError`: If build fails

**Side Effects**: None (pure function)

---

#### `get_vector(identity_hash: str) -> ConsequenceVector`

Gets consequence vector for identity.

**Parameters**:
- `identity_hash`: Identity hash string (64 hex chars)

**Returns**: `ConsequenceVector` dict with:
- `out_degree`: int
- `k_reach`: int
- `survival`: float [0.0, 1.0]
- `entropy`: float >= 0.0
- `escape_concentration`: float [0.0, 1.0]
- `near_refusal_rate`: float [0.0, 1.0]
- `dead_end_risk`: float [0.0, 1.0]

**Raises**:
- `KeyError`: If identity_hash not found
- `ConsequenceFieldError`: If vector not computed

---

#### `get_delta(transition: Tuple[str, str]) -> ConsequenceDelta`

Gets counterfactual delta for transition.

**Parameters**:
- `transition`: (source_hash, target_hash) tuple

**Returns**: `ConsequenceDelta` dict with:
- `survival_delta`: float
- `k_reach_delta`: int
- `entropy_delta`: float
- `refusal_delta`: float

**Raises**:
- `KeyError`: If transition not found
- `ConsequenceFieldError`: If delta not computed

---

## Phase 6: Meaning Discovery Engine

### MeaningDiscoveryEngine

**Constructor**:
```python
def __init__(
    self,
    consequence_field: ConsequenceField,
    config: Optional[Dict[str, Any]] = None
) -> None
```

**Methods**:

#### `discover(num_clusters: Optional[int] = None) -> MeaningMap`

Discovers meaning clusters from consequence vectors.

**Parameters**:
- `num_clusters`: Number of clusters (None = auto-detect)

**Returns**: `MeaningMap` object

**Raises**:
- `MeaningDiscoveryError`: If discovery fails

---

## Phase 7: Role Emergence Engine

### RoleEmergenceEngine

**Constructor**:
```python
def __init__(
    self,
    meaning_map: MeaningMap,
    consequence_field: ConsequenceField,
    config: Optional[Dict[str, Any]] = None
) -> None
```

**Methods**:

#### `emerge() -> RoleMap`

Emerges functional roles from meaning clusters.

**Returns**: `RoleMap` object

**Raises**:
- `RoleEmergenceError`: If emergence fails

---

## Phase 8: Constraint Discovery Engine

### ConstraintDiscoveryEngine

**Constructor**:
```python
def __init__(
    self,
    roles: RoleMap,
    symbol_sequences: List[List[int]],
    edge_deltas: Dict[Tuple[str, str], Dict[str, float]],
    config: Optional[Dict[str, Any]] = None
) -> None
```

**Methods**:

#### `discover(min_frequency: int = 3) -> ConstraintMap`

Discovers constraints and templates.

**Parameters**:
- `min_frequency`: Minimum pattern frequency (default: 3)

**Returns**: `ConstraintMap` object

**Raises**:
- `ConstraintDiscoveryError`: If discovery fails

---

## Phase 9: Fluency Generator

### FluencyGenerator

**Constructor**:
```python
def __init__(
    self,
    consequence_field: ConsequenceField,
    roles: RoleMap,
    constraints: ConstraintMap,
    phase3_relations: Dict[str, Any],
    phase4_symbols: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> None
```

**Methods**:

#### `generate(start_symbol: int, length: int = 50) -> str`

Generates fluent text sequence.

**Parameters**:
- `start_symbol`: Starting symbol ID
- `length`: Desired sequence length

**Returns**: Generated text string

**Raises**:
- `FluencyGenerationError`: If generation fails

---

## Data Types

### ConsequenceVector

```python
from typing import TypedDict

class ConsequenceVector(TypedDict):
    out_degree: int
    k_reach: int
    survival: float
    entropy: float
    escape_concentration: float
    near_refusal_rate: float
    dead_end_risk: float
```

### ConsequenceDelta

```python
class ConsequenceDelta(TypedDict):
    survival_delta: float
    k_reach_delta: int
    entropy_delta: float
    refusal_delta: float
```

### MeaningSignature

```python
class MeaningSignature(TypedDict):
    centroid: Dict[str, float]
    size: int
    identities: List[str]
```

---

## Error Conditions

### Common Errors

1. **Invalid Input**: Wrong type or format
2. **Missing Data**: Required phase output not found
3. **Computation Failure**: Algorithm error
4. **Resource Exhaustion**: Memory or time limits

### Error Handling

All errors raise specific exceptions with clear messages:

```python
try:
    vector = engine.get_vector(identity_hash)
except KeyError as e:
    logger.error(f"Identity not found: {identity_hash}")
    raise ConsequenceFieldError(f"Identity not in field: {identity_hash}") from e
```

---

## Performance Contracts

### Time Complexity

- Phase 5: O(n * k * r) where n=identities, k=horizon, r=rollouts
- Phase 6: O(n * log(n)) for clustering
- Phase 7: O(n) for role assignment
- Phase 8: O(m * p) where m=sequences, p=pattern_length
- Phase 9: O(l * a) where l=length, a=allowed_transitions

### Space Complexity

- Phase 5: O(n * d) where d=vector_dimension
- Phase 6: O(n + c) where c=clusters
- Phase 7: O(n)
- Phase 8: O(p) where p=patterns
- Phase 9: O(l)

---

## Versioning

### API Versioning

- Current: v1.0.0
- Breaking changes: Increment major version
- New features: Increment minor version
- Bug fixes: Increment patch version

---

**End of Contracts Document**
