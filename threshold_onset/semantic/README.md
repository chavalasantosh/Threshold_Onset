# Semantic Discovery Module

**Enterprise-Grade Semantic Understanding System**

## Overview

The Semantic Discovery Module implements automatic semantic understanding and fluent output generation from first principles, built on the frozen structure foundation (Phases 0-4).

**Status**: 🟡 Active Development  
**Foundation**: Phases 0-4 (FROZEN)  
**Standards**: Enterprise MNC-grade code quality

**⚠️ IMPORTANT**: See `CORRECTIONS_APPLIED.md` and `PHASE5_CORRECTED_SPEC.md` for critical corrections that address hidden imports and engineering bugs.

---

## Architecture

### Module Structure

```
semantic/
├── __init__.py                 # Module exports
├── README.md                   # This file
├── ARCHITECTURE.md             # Detailed architecture
├── CONTRACTS.md                # API contracts and interfaces
├── phase5/                     # Consequence Field Engine
│   ├── __init__.py
│   ├── consequence_field.py   # Main engine
│   ├── rollout.py              # Rollout measurement
│   ├── metrics.py               # Consequence metrics
│   └── README.md
├── phase6/                     # Meaning Discovery
│   ├── __init__.py
│   ├── meaning_discovery.py    # Main engine
│   ├── clustering.py           # Vector clustering
│   └── README.md
├── phase7/                     # Role Emergence
│   ├── __init__.py
│   ├── role_emergence.py       # Main engine
│   ├── role_assigner.py        # Role assignment
│   └── README.md
├── phase8/                     # Constraint Discovery
│   ├── __init__.py
│   ├── constraint_discovery.py # Main engine
│   ├── pattern_miner.py         # Pattern mining
│   └── README.md
├── phase9/                     # Fluency Generator
│   ├── __init__.py
│   ├── fluency_generator.py    # Main generator
│   ├── scoring.py               # Revised scoring
│   └── README.md
├── common/                     # Shared utilities
│   ├── __init__.py
│   ├── types.py                 # Type definitions
│   ├── exceptions.py            # Custom exceptions
│   ├── validators.py            # Input validation
│   └── utils.py                 # Utility functions
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_phase5.py
│   ├── test_phase6.py
│   ├── test_phase7.py
│   ├── test_phase8.py
│   └── test_phase9.py
└── config/                      # Configuration
    ├── __init__.py
    ├── defaults.py              # Default parameters
    └── validation.py            # Config validation
```

---

## Phases

### Phase 5: Consequence Field Engine

**Purpose**: Measure how structures affect future possibilities

**Key Components**:
- Rollout-based measurement
- k-step reachability
- Survival probability
- Refusal proximity
- Dead-end risk

**Deliverable**: `consequence_field.json`

---

### Phase 6: Meaning Discovery

**Purpose**: Cluster consequence vectors to discover meaning signatures

**Key Components**:
- Vector normalization
- k-medoids clustering
- Meaning signature extraction

**Deliverable**: `meaning_map.json`

---

### Phase 7: Role Emergence

**Purpose**: Discover functional roles from cluster properties

**Key Components**:
- Cluster property computation
- Quantile-based role assignment
- Functional role mapping

**Deliverable**: `roles.json`

---

### Phase 8: Constraint Discovery

**Purpose**: Discover grammar-like constraints from role patterns

**Key Components**:
- Role sequence extraction
- Pattern mining
- Forbidden pattern discovery
- Template building

**Deliverable**: `constraints.json`

---

### Phase 9: Fluency Generator

**Purpose**: Generate fluent sequences using stability + novelty

**Key Components**:
- Stability scoring
- Template satisfaction
- Novelty constraint
- Revised path scoring

**Deliverable**: Fluent text output

---

## Code Standards

### Enterprise Requirements

1. **Type Hints**: All functions must have type annotations
2. **Docstrings**: Google-style docstrings for all public APIs
3. **Error Handling**: Comprehensive exception handling
4. **Logging**: Structured logging for all operations
5. **Validation**: Input validation for all public methods
6. **Testing**: Unit tests with >80% coverage
7. **Documentation**: Complete API documentation
8. **Versioning**: Semantic versioning
9. **Configuration**: Externalized configuration
10. **Performance**: Optimized for production use

---

## Dependencies

### Core Dependencies
- Python 3.8+
- Standard library only (no external AI/ML libraries)

### Optional Dependencies
- `numpy` (for vector operations, if needed)
- `scipy` (for clustering algorithms, if needed)

**Note**: All algorithms are implemented from first principles. External libraries are optional optimizations only.

---

## Usage

### Basic Usage

```python
from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)

# Phase 5: Build consequence field
consequence_engine = ConsequenceFieldEngine(
    phase2_identities=phase2_metrics,
    phase3_relations=phase3_metrics,
    phase4_symbols=phase4_output
)
consequence_field = consequence_engine.build()

# Phase 6: Discover meaning
meaning_engine = MeaningDiscoveryEngine(consequence_field)
meaning_map = meaning_engine.discover()

# Phase 7: Emerge roles
role_engine = RoleEmergenceEngine(meaning_map, consequence_field)
roles = role_engine.emerge()

# Phase 8: Discover constraints
constraint_engine = ConstraintDiscoveryEngine(roles, symbol_sequences)
constraints = constraint_engine.discover()

# Phase 9: Generate fluent text
generator = FluencyGenerator(
    consequence_field=consequence_field,
    roles=roles,
    constraints=constraints
)
fluent_text = generator.generate(start_symbol, length=50)
```

---

## Testing

### Run All Tests

```bash
pytest tests/semantic/ -v --cov=threshold_onset.semantic --cov-report=html
```

### Run Specific Phase Tests

```bash
pytest tests/semantic/test_phase5.py -v
```

---

## Documentation

- **ARCHITECTURE.md**: Detailed system architecture
- **CONTRACTS.md**: API contracts and interfaces
- **Phase READMEs**: Individual phase documentation

---

## Contributing

See `CONTRIBUTING.md` in project root for contribution guidelines.

---

## License

MIT License - See LICENSE file in project root.

---

## Version

**Current Version**: 1.0.0  
**Status**: Active Development  
**Last Updated**: 2025-01-13
