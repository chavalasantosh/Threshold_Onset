# Semantic Discovery Module - Complete Execution Guide

**Enterprise Execution Guide with All Code**

## Overview

Complete execution guide for the Semantic Discovery Module (Phases 5-9) with all code examples ready to run.

**Status**: ✅ **ALL PHASES COMPLETE - READY TO EXECUTE**

---

## Prerequisites

### 1. Install Dependencies

```bash
# Install pytest for testing (optional)
pip install pytest pytest-cov

# No other dependencies required - uses Python standard library only
```

### 2. Verify Installation

```bash
# Test import
python -c "from threshold_onset.semantic import ConsequenceFieldEngine; print('✓ Import successful')"
```

---

## Complete Execution Code

### Option 1: Use Example Workflow Script

**File**: `threshold_onset/semantic/example_complete_workflow.py`

```bash
# Run complete workflow
python threshold_onset/semantic/example_complete_workflow.py
```

### Option 2: Complete Python Script (Copy-Paste Ready)

```python
#!/usr/bin/env python3
"""
Complete Semantic Discovery Workflow
Execute all phases from Phase 5 to Phase 9
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def execute_complete_workflow():
    """
    Execute complete semantic discovery workflow.
    
    Replace the placeholder data with your actual Phase 2-4 outputs.
    """
    logger.info("=" * 60)
    logger.info("Semantic Discovery Module - Complete Workflow")
    logger.info("=" * 60)

    # ============================================================
    # STEP 1: Load Your Phase 2-4 Outputs
    # ============================================================
    # REPLACE THESE with your actual outputs from Phases 0-4
    
    phase2_metrics = {
        # Your Phase 2 identity metrics
        # Example structure:
        # 'identities': {
        #     'identity_hash_1': {'count': 5, ...},
        #     'identity_hash_2': {'count': 3, ...}
        # },
        # 'identity_hashes': ['identity_hash_1', 'identity_hash_2', ...]
    }

    phase3_metrics = {
        # Your Phase 3 relation metrics
        # Example structure:
        # 'graph_nodes': {'identity_hash_1', 'identity_hash_2', ...},
        # 'graph_edges': {('identity_hash_1', 'identity_hash_2'), ...},
        # 'relations': {...}
    }

    phase4_output = {
        # Your Phase 4 symbol mappings
        # Example structure:
        # 'identity_to_symbol': {
        #     'identity_hash_1': 0,
        #     'identity_hash_2': 1,
        #     ...
        # },
        # 'symbol_to_identity': {
        #     0: 'identity_hash_1',
        #     1: 'identity_hash_2',
        #     ...
        # }
    }

    symbol_sequences = [
        # Your symbol sequences for training
        # Example: [[0, 1, 2], [1, 2, 3], [2, 3, 0], ...]
    ]

    # ============================================================
    # STEP 2: Setup Continuation Observer
    # ============================================================
    logger.info("\n[SETUP] Initializing ContinuationObserver...")

    try:
        from integration.continuation_observer import ContinuationObserver
        observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)
        logger.info("✓ ContinuationObserver initialized")
    except ImportError as e:
        logger.error("Failed to import ContinuationObserver: %s", e)
        logger.info("Skipping - ContinuationObserver not available")
        logger.info("You may need to create a mock observer for testing")
        return
    except (AttributeError, TypeError, ValueError) as e:
        logger.error("Failed to initialize observer: %s", e)
        return

    # ============================================================
    # STEP 3: PHASE 5 - CONSEQUENCE FIELD ENGINE
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 5: Consequence Field Engine")
    logger.info("=" * 60)

    try:
        consequence_engine = ConsequenceFieldEngine(
            phase2_identities=phase2_metrics,
            phase3_relations=phase3_metrics,
            phase4_symbols=phase4_output,
            continuation_observer=observer
        )

        logger.info("Building consequence field (k=5, rollouts=100)...")
        consequence_field = consequence_engine.build(
            k=5,
            num_rollouts=100,
            seed=42
        )

        logger.info(
            "✓ Consequence field built: %d identities",
            len(consequence_field.identity_vectors)
        )
        logger.info("  Edge deltas: %d", len(consequence_field.edge_deltas))

        # Save intermediate result
        consequence_engine.save('consequence_field.json')
        logger.info("✓ Saved to consequence_field.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 5 failed: %s", e)
        return

    # ============================================================
    # STEP 4: PHASE 6 - MEANING DISCOVERY
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 6: Meaning Discovery")
    logger.info("=" * 60)

    try:
        meaning_engine = MeaningDiscoveryEngine(consequence_field)

        logger.info("Discovering meaning clusters...")
        meaning_map = meaning_engine.discover(seed=42)

        logger.info("✓ Meaning discovered: %d clusters", len(meaning_map.clusters))
        for cluster_id, signature in meaning_map.clusters.items():
            logger.info("  %s: size=%d", cluster_id, signature.size)

        # Save intermediate result
        meaning_engine.save('meaning_map.json')
        logger.info("✓ Saved to meaning_map.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 6 failed: %s", e)
        return

    # ============================================================
    # STEP 5: PHASE 7 - ROLE EMERGENCE
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 7: Role Emergence")
    logger.info("=" * 60)

    try:
        role_engine = RoleEmergenceEngine(
            meaning_map=meaning_map,
            consequence_field=consequence_field,
            continuation_observer=observer
        )

        logger.info("Emerging functional roles...")
        roles = role_engine.emerge()

        logger.info("✓ Roles emerged: %d role assignments", len(roles['cluster_roles']))
        for cluster_id, role in roles['cluster_roles'].items():
            logger.info("  %s: %s", cluster_id, role)

        # Save intermediate result
        role_engine.save('roles.json')
        logger.info("✓ Saved to roles.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 7 failed: %s", e)
        return

    # ============================================================
    # STEP 6: PHASE 8 - CONSTRAINT DISCOVERY
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 8: Constraint Discovery")
    logger.info("=" * 60)

    try:
        constraint_engine = ConstraintDiscoveryEngine(
            roles=roles,
            symbol_sequences=symbol_sequences,
            edge_deltas=consequence_field.edge_deltas,
            continuation_observer=observer,
            identity_to_symbol=phase4_output.get('identity_to_symbol', {})
        )

        logger.info("Discovering constraints and templates...")
        constraints = constraint_engine.discover()

        logger.info("✓ Constraints discovered:")
        logger.info("  Patterns: %d", len(constraints['role_patterns']))
        logger.info("  Forbidden: %d", len(constraints['forbidden_patterns']))
        logger.info("  Templates: %d", len(constraints['templates']))

        # Save intermediate result
        constraint_engine.save('constraints.json')
        logger.info("✓ Saved to constraints.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 8 failed: %s", e)
        return

    # ============================================================
    # STEP 7: PHASE 9 - FLUENCY GENERATOR
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 9: Fluency Generator")
    logger.info("=" * 60)

    try:
        generator = FluencyGenerator(
            consequence_field=consequence_field,
            roles=roles,
            constraints=constraints,
            phase3_relations=phase3_metrics,
            phase4_symbols=phase4_output,
            continuation_observer=observer
        )

        logger.info("Building experience table...")
        generator.build_experience_table()
        logger.info("✓ Experience table built: %d entries", len(generator.experience_table))

        logger.info("Generating fluent sequence...")
        sequence = generator.generate(
            start_symbol=0,
            length=50,
            seed=42
        )

        logger.info("✓ Generated sequence: %d symbols", len(sequence))
        logger.info("  Sequence: %s...", sequence[:10])  # Show first 10

        # Optional: Generate text if you have symbol-to-text mapping
        # symbol_to_text = {
        #     0: 'hello',
        #     1: 'world',
        #     ...
        # }
        # text = generator.generate_text(
        #     start_symbol=0,
        #     length=50,
        #     symbol_to_text=symbol_to_text,
        #     seed=42
        # )
        # logger.info("✓ Generated text: %s", text)

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 9 failed: %s", e)
        return

    # ============================================================
    # COMPLETE
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("✅ COMPLETE WORKFLOW FINISHED")
    logger.info("=" * 60)
    logger.info("\nGenerated files:")
    logger.info("  - consequence_field.json")
    logger.info("  - meaning_map.json")
    logger.info("  - roles.json")
    logger.info("  - constraints.json")
    logger.info("\nAll phases completed successfully!")


if __name__ == '__main__':
    execute_complete_workflow()
```

**Save this as**: `run_semantic_discovery.py`

**Execute**:
```bash
python run_semantic_discovery.py
```

---

## Individual Phase Execution

### Phase 5 Only

```python
from threshold_onset.semantic import ConsequenceFieldEngine

# Your Phase 2-4 outputs
phase2_metrics = {...}
phase3_metrics = {...}
phase4_output = {...}

# Create observer
from integration.continuation_observer import ContinuationObserver
observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

# Build consequence field
engine = ConsequenceFieldEngine(
    phase2_identities=phase2_metrics,
    phase3_relations=phase3_metrics,
    phase4_symbols=phase4_output,
    continuation_observer=observer
)

consequence_field = engine.build(k=5, num_rollouts=100, seed=42)
engine.save('consequence_field.json')
print(f"✓ Built: {len(consequence_field.identity_vectors)} identities")
```

### Phase 6 Only

```python
from threshold_onset.semantic import MeaningDiscoveryEngine

# Load from Phase 5 output
from threshold_onset.semantic.common.types import ConsequenceField
import json

with open('consequence_field.json', 'r') as f:
    data = json.load(f)
    consequence_field = ConsequenceField(**data)

# Discover meaning
engine = MeaningDiscoveryEngine(consequence_field)
meaning_map = engine.discover(seed=42)
engine.save('meaning_map.json')
print(f"✓ Discovered: {len(meaning_map.clusters)} clusters")
```

### Phase 7 Only

```python
from threshold_onset.semantic import RoleEmergenceEngine

# Load from previous phases
# ... (load consequence_field and meaning_map)

engine = RoleEmergenceEngine(
    meaning_map=meaning_map,
    consequence_field=consequence_field,
    continuation_observer=observer
)
roles = engine.emerge()
engine.save('roles.json')
print(f"✓ Emerged: {len(roles['cluster_roles'])} roles")
```

### Phase 8 Only

```python
from threshold_onset.semantic import ConstraintDiscoveryEngine

# Load from previous phases
# ... (load roles, consequence_field, symbol_sequences)

engine = ConstraintDiscoveryEngine(
    roles=roles,
    symbol_sequences=symbol_sequences,
    edge_deltas=consequence_field.edge_deltas,
    continuation_observer=observer,
    identity_to_symbol=phase4_output.get('identity_to_symbol', {})
)
constraints = engine.discover()
engine.save('constraints.json')
print(f"✓ Discovered: {len(constraints['templates'])} templates")
```

### Phase 9 Only

```python
from threshold_onset.semantic import FluencyGenerator

# Load from previous phases
# ... (load all previous outputs)

generator = FluencyGenerator(
    consequence_field=consequence_field,
    roles=roles,
    constraints=constraints,
    phase3_relations=phase3_metrics,
    phase4_symbols=phase4_output,
    continuation_observer=observer
)

generator.build_experience_table()
sequence = generator.generate(start_symbol=0, length=50, seed=42)
print(f"✓ Generated: {len(sequence)} symbols")
print(f"  Sequence: {sequence[:10]}")
```

---

## Testing Execution

### Run All Tests

```bash
# From project root
pytest threshold_onset/semantic/tests/ -v

# With coverage
pytest threshold_onset/semantic/tests/ \
    --cov=threshold_onset.semantic \
    --cov-report=html \
    --cov-report=term-missing
```

### Run Specific Phase Tests

```bash
# Phase 5
pytest threshold_onset/semantic/tests/test_phase5.py -v

# Phase 6
pytest threshold_onset/semantic/tests/test_phase6.py -v

# Phase 7
pytest threshold_onset/semantic/tests/test_phase7.py -v

# Phase 8
pytest threshold_onset/semantic/tests/test_phase8.py -v

# Phase 9
pytest threshold_onset/semantic/tests/test_phase9.py -v

# Integration
pytest threshold_onset/semantic/tests/test_integration.py -v
```

---

## Configuration Options

### Custom Configuration

```python
from threshold_onset.semantic.config.defaults import (
    DEFAULT_K,
    DEFAULT_NUM_ROLLOUTS,
    DEFAULT_MAX_STEPS
)

# Custom config
config = {
    'phase5': {
        'k': 7,  # k-step horizon (default: 5)
        'num_rollouts': 200,  # Number of rollouts (default: 100)
        'max_steps': 100  # Max rollout steps (default: 50)
    },
    'phase6': {
        'k_min': 2,  # Min clusters
        'k_max': 10  # Max clusters
    },
    'phase9': {
        'stability_weight': 0.4,
        'template_weight': 0.3,
        'novelty_window': 5
    }
}

# Use in engine
consequence_engine = ConsequenceFieldEngine(
    phase2_identities=phase2_metrics,
    phase3_relations=phase3_metrics,
    phase4_symbols=phase4_output,
    continuation_observer=observer,
    config=config
)
```

---

## Output Files

After execution, you'll have:

1. **consequence_field.json** - Phase 5 output
   - Identity vectors
   - Edge deltas
   - Metadata

2. **meaning_map.json** - Phase 6 output
   - Clusters
   - Identity-to-cluster mapping
   - Signatures

3. **roles.json** - Phase 7 output
   - Symbol-to-role mapping
   - Cluster roles
   - Role properties

4. **constraints.json** - Phase 8 output
   - Role patterns
   - Forbidden patterns
   - Templates

---

## Troubleshooting

### Import Errors

```bash
# If imports fail, ensure you're in project root
cd /path/to/THRESHOLD_ONSET

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Missing ContinuationObserver

```python
# Create a mock observer for testing
class MockObserver:
    def __init__(self):
        self.adjacency = {
            'id1': {'id2', 'id3'},
            'id2': {'id3'},
            'id3': set()
        }
    
    def _check_transition_allowed(self, source, target):
        return target in self.adjacency.get(source, set())
    
    def _identity_hash_to_symbol(self, identity_hash):
        return hash(identity_hash) % 1000

observer = MockObserver()
```

### Empty Data

```python
# If you don't have Phase 2-4 outputs yet, create minimal test data
phase2_metrics = {
    'identities': {
        'id1': {'count': 1},
        'id2': {'count': 1}
    }
}

phase3_metrics = {
    'graph_nodes': {'id1', 'id2'},
    'graph_edges': {('id1', 'id2')}
}

phase4_output = {
    'identity_to_symbol': {'id1': 0, 'id2': 1},
    'symbol_to_identity': {0: 'id1', 1: 'id2'}
}

symbol_sequences = [[0, 1], [1, 0]]
```

---

## Quick Reference

### All Imports

```python
from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)
from threshold_onset.semantic.common.types import (
    ConsequenceField,
    MeaningMap,
    RoleMap,
    ConstraintMap
)
```

### All Execution Commands

```bash
# Run complete workflow
python threshold_onset/semantic/example_complete_workflow.py

# Run tests
pytest threshold_onset/semantic/tests/ -v

# Run specific phase test
pytest threshold_onset/semantic/tests/test_phase5.py -v

# Check imports
python -c "from threshold_onset.semantic import ConsequenceFieldEngine; print('OK')"
```

---

## Next Steps

1. **Replace placeholder data** with your actual Phase 2-4 outputs
2. **Run the complete workflow** script
3. **Check generated JSON files** for results
4. **Run tests** to verify everything works
5. **Customize configuration** as needed

---

**Ready to Execute!**

All code is ready to copy-paste and run. Just replace the placeholder data with your actual Phase 2-4 outputs.

---

**End of Execution Guide**
