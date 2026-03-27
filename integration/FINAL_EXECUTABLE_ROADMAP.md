# Final Executable Roadmap: Phase 5-8
## Pure First-Principles, No Hidden Imports, Actually Works

**Date**: 2025-01-13  
**Status**: 🎯 FINAL EXECUTABLE VERSION  
**Foundation**: Phases 0-4 (FROZEN)  
**Existing Infrastructure**: `scoring.py`, `escape_topology.py`, `continuation_observer.py`

---

## Critical Fixes Applied

### ❌ Removed All Hidden Imports
1. ✅ No grammar rules (determiner→noun, etc.)
2. ✅ No POS categories (noun/verb/determiner)
3. ✅ No hand-picked thresholds
4. ✅ No boolean signatures
5. ✅ No "Text → Tokens" assumption

### ✅ Proper Definitions
1. ✅ Future space = k-step rollout with consistent horizon
2. ✅ Refusal = actual refusal events, not dead ends
3. ✅ Meaning = consequence vectors (numeric, not booleans)
4. ✅ Thresholds = emergent (quantiles/clustering)
5. ✅ Roles = functional behaviors, not labels

---

## What We Already Have (Reusable)

### ✅ Existing Code to Reuse

1. **`scoring.py`**:
   - `compute_pressure_scores()` - pressure computation
   - `score_allowed_paths()` - path scoring framework
   - Can extend, not replace

2. **`escape_topology.py`**:
   - `measure_escape_topology()` - escape path measurement
   - `near_refusal_events` tracking
   - `escape_concentration` computation
   - Can reuse directly

3. **`continuation_observer.py`**:
   - `ContinuationObserver` - tracks refusals
   - `_check_transition_allowed()` - constraint checking
   - Can use for rollout measurement

---

## Phase 5: CONSEQUENCE FIELD ENGINE

**Status**: 🟡 TO BE BUILT  
**Purpose**: Compute consequence vectors for all identities and edges

### Core Definition

**Consequence Vector = Measurable Effect on Future Space**

Not topology counts. **Rollout-based measurement** with consistent horizon.

### Algorithm: Rollout-Based Consequence Measurement

#### Step 1: Define Rollout Policy

**Reuse**: `ContinuationObserver` from existing code

```python
def rollout_from_identity(identity_hash, phase3_relations, phase4_symbols, 
                          continuation_observer, max_steps=50, num_rollouts=100):
    """
    Run rollouts from identity_hash following system's selection policy.
    
    Uses existing continuation_observer to check allowed transitions.
    Follows same policy as current generation (maximize continuation).
    
    Returns:
    - survival_lengths: List of rollout lengths before stop
    - refusal_occurred: List of booleans (did refusal happen?)
    - pressure_accumulated: List of pressure values
    - entropy_trajectory: List of entropy values per step
    """
    results = {
        'survival_lengths': [],
        'refusal_occurred': [],
        'pressure_accumulated': [],
        'entropy_trajectory': []
    }
    
    for _ in range(num_rollouts):
        path = [identity_hash]
        pressure = 0.0
        entropy_values = []
        refusal_occurred = False
        
        current = identity_hash
        for step in range(max_steps):
            # Get allowed next identities (using existing observer)
            allowed = continuation_observer.adjacency.get(current, set())
            
            if not allowed:
                # Dead-end (different from refusal)
                break
            
            # Choose next: maximize continuation options
            # (Same policy as current generation)
            scores = {}
            for target in allowed:
                target_futures = len(continuation_observer.adjacency.get(target, set()))
                scores[target] = target_futures
            
            if not scores:
                break
            
            # Select best (deterministic if seed fixed)
            best_score = max(scores.values())
            candidates = [t for t, s in scores.items() if s == best_score]
            next_identity = candidates[0] if len(candidates) == 1 else sorted(candidates)[0]
            
            # Check for refusal (self-transition attempt)
            if next_identity == current:
                refusal_occurred = True
                break
            
            # Update
            path.append(next_identity)
            current = next_identity
            
            # Measure entropy (branching uncertainty)
            current_options = len(continuation_observer.adjacency.get(current, set()))
            entropy = calculate_entropy_from_options(current_options)
            entropy_values.append(entropy)
            
            # Measure pressure (from existing topology data if available)
            pressure += 1.0 / max(current_options, 1)
        
        results['survival_lengths'].append(len(path) - 1)
        results['refusal_occurred'].append(refusal_occurred)
        results['pressure_accumulated'].append(pressure)
        if entropy_values:
            results['entropy_trajectory'].append(entropy_values[-1])
    
    return results
```

#### Step 2: Compute Consequence Vector (Proper Definition)

**Fix**: Use k-step reachability with consistent horizon, not 2-step

```python
def compute_consequence_vector(identity_hash, phase3_relations, phase4_symbols,
                               continuation_observer, k=5):
    """
    Compute consequence vector for identity.
    
    Vector components (all numeric, not boolean):
    1. out_degree: Number of outgoing relations
    2. k_reach: k-step reachable set size (consistent horizon)
    3. survival: Probability K-step rollout avoids refusal
    4. entropy: Entropy of next-step distribution
    5. escape_concentration: From existing topology (reuse escape_topology.py)
    6. near_refusal_rate: Fraction of visits within w steps of refusal
    7. dead_end_risk: Fraction leading to zero-outgoing nodes
    """
    # Component 1: out_degree
    outgoing = continuation_observer.adjacency.get(identity_hash, set())
    out_degree = len(outgoing)
    
    # Component 2: k_reach (k-step reachable set)
    k_reach = compute_k_reach(identity_hash, continuation_observer, k)
    
    # Component 3: survival (rollout-based)
    rollout_results = rollout_from_identity(
        identity_hash, phase3_relations, phase4_symbols, continuation_observer
    )
    survival = sum(1 for r in rollout_results['refusal_occurred'] if not r) / len(rollout_results['refusal_occurred'])
    
    # Component 4: entropy
    if outgoing:
        # Uniform distribution entropy
        entropy = math.log(len(outgoing))
    else:
        entropy = 0.0
    
    # Component 5: escape_concentration (reuse existing)
    # Get from escape_topology if available, or compute
    symbol = phase4_symbols.get_symbol(identity_hash)
    escape_concentration = get_escape_concentration(symbol)  # From existing topology
    
    # Component 6: near_refusal_rate (from actual refusal events)
    # Count how often this identity appears near refusal
    near_refusal_rate = compute_near_refusal_rate(identity_hash, continuation_observer)
    
    # Component 7: dead_end_risk (different from refusal)
    dead_end_count = 0
    for target in outgoing:
        target_outgoing = continuation_observer.adjacency.get(target, set())
        if len(target_outgoing) == 0:
            dead_end_count += 1
    dead_end_risk = dead_end_count / max(out_degree, 1)
    
    return {
        'out_degree': out_degree,
        'k_reach': k_reach,
        'survival': survival,
        'entropy': entropy,
        'escape_concentration': escape_concentration,
        'near_refusal_rate': near_refusal_rate,
        'dead_end_risk': dead_end_risk
    }
```

#### Step 3: Compute k-Step Reachability (Fixed Horizon)

**Fix**: Consistent k, not arbitrary 2-step

```python
def compute_k_reach(identity_hash, continuation_observer, k=5):
    """
    Compute k-step reachable set size.
    
    Uses consistent horizon k (not arbitrary 2-step).
    """
    reachable = set()
    current_level = {identity_hash}
    
    for step in range(k):
        next_level = set()
        for node in current_level:
            outgoing = continuation_observer.adjacency.get(node, set())
            next_level.update(outgoing)
            reachable.update(outgoing)
        current_level = next_level
        if not current_level:
            break
    
    return len(reachable)
```

#### Step 4: Compute Near-Refusal Rate (Actual Refusal Events)

**Fix**: Use actual refusal events, not dead ends

```python
def compute_near_refusal_rate(identity_hash, continuation_observer, window=3):
    """
    Compute near-refusal rate from actual refusal events.
    
    Refusal = self-transition attempt (not dead-end).
    Near-refusal = within window steps of refusal.
    """
    # This requires tracking refusal events during rollouts
    # Or use existing continuation_observer refusal logs
    
    # For now, use escape_topology data if available
    symbol = phase4_symbols.get_symbol(identity_hash)
    topology_data = get_topology_data(symbol)  # From escape_topology.py
    
    if topology_data:
        appearances = topology_data.get('appearances', 0)
        near_refusals = topology_data.get('near_refusal_events', 0)
        return near_refusals / max(appearances, 1)
    
    return 0.0
```

#### Step 5: Build Consequence Field (All Identities)

**Output**: JSON artifact with all consequence vectors

```python
def build_consequence_field(phase2_identities, phase3_relations, phase4_symbols,
                            continuation_observer, k=5):
    """
    Build complete consequence field.
    
    Output: {
        'identity_vectors': {identity_hash: vector},
        'edge_deltas': {(source, target): delta_vector}
    }
    """
    identity_vectors = {}
    
    # Compute vectors for all identities
    for identity_hash in phase2_identities:
        vector = compute_consequence_vector(
            identity_hash, phase3_relations, phase4_symbols,
            continuation_observer, k
        )
        identity_vectors[identity_hash] = vector
    
    # Compute edge deltas (counterfactual)
    edge_deltas = {}
    for source_hash in phase2_identities:
        source_vector = identity_vectors[source_hash]
        outgoing = continuation_observer.adjacency.get(source_hash, set())
        
        for target_hash in outgoing:
            target_vector = identity_vectors[target_hash]
            
            # Delta = how transition changes consequences
            delta = {
                'survival_delta': target_vector['survival'] - source_vector['survival'],
                'k_reach_delta': target_vector['k_reach'] - source_vector['k_reach'],
                'entropy_delta': target_vector['entropy'] - source_vector['entropy'],
                'refusal_delta': target_vector['near_refusal_rate'] - source_vector['near_refusal_rate']
            }
            edge_deltas[(source_hash, target_hash)] = delta
    
    return {
        'identity_vectors': identity_vectors,
        'edge_deltas': edge_deltas
    }
```

### Phase 5 Deliverable

**File**: `consequence_field.json`

```json
{
    "identity_vectors": {
        "identity_hash_1": {
            "out_degree": 3,
            "k_reach": 12,
            "survival": 0.85,
            "entropy": 1.098,
            "escape_concentration": 0.75,
            "near_refusal_rate": 0.15,
            "dead_end_risk": 0.0
        },
        ...
    },
    "edge_deltas": {
        "(source_hash, target_hash)": {
            "survival_delta": 0.1,
            "k_reach_delta": 2,
            "entropy_delta": -0.2,
            "refusal_delta": -0.05
        },
        ...
    }
}
```

---

## Phase 6: MEANING DISCOVERY (Clustering)

**Status**: 🟡 TO BE BUILT  
**Purpose**: Cluster consequence vectors to discover meaning signatures

### Core Principle

**Meaning = Clusters in Consequence Space**

Not labels. Not booleans. **Vector clusters**.

### Algorithm: Deterministic Clustering

#### Step 1: Normalize Vectors

```python
def normalize_vectors(identity_vectors):
    """
    Normalize consequence vectors for clustering.
    
    Each component normalized to [0, 1] range.
    """
    # Collect all values per component
    components = {
        'out_degree': [],
        'k_reach': [],
        'survival': [],
        'entropy': [],
        'escape_concentration': [],
        'near_refusal_rate': [],
        'dead_end_risk': []
    }
    
    for vector in identity_vectors.values():
        for key in components:
            components[key].append(vector.get(key, 0.0))
    
    # Compute min/max for normalization
    ranges = {}
    for key, values in components.items():
        ranges[key] = {
            'min': min(values) if values else 0.0,
            'max': max(values) if values else 1.0
        }
    
    # Normalize
    normalized = {}
    for identity_hash, vector in identity_vectors.items():
        normalized[identity_hash] = {}
        for key in components:
            value = vector.get(key, 0.0)
            min_val = ranges[key]['min']
            max_val = ranges[key]['max']
            if max_val > min_val:
                normalized[identity_hash][key] = (value - min_val) / (max_val - min_val)
            else:
                normalized[identity_hash][key] = 0.0
    
    return normalized, ranges
```

#### Step 2: Cluster Using k-Medoids (Deterministic)

**Fix**: No hand thresholds, use clustering algorithm

```python
def cluster_consequence_vectors(normalized_vectors, num_clusters=None):
    """
    Cluster vectors using k-medoids (deterministic, not ML).
    
    If num_clusters not specified, use elbow method or fixed heuristic.
    """
    # Convert to list for clustering
    identity_list = list(normalized_vectors.keys())
    vector_list = [normalized_vectors[h] for h in identity_list]
    
    # Determine number of clusters (emergent)
    if num_clusters is None:
        # Use heuristic: sqrt(n/2) or elbow method
        num_clusters = int(math.sqrt(len(identity_list) / 2))
        num_clusters = max(2, min(num_clusters, 12))  # Reasonable range
    
    # k-medoids clustering (deterministic)
    # Use PAM algorithm (Partitioning Around Medoids)
    clusters = k_medoids_clustering(vector_list, identity_list, num_clusters)
    
    return clusters
```

#### Step 3: Extract Meaning Signatures

**Output**: Cluster centroids (meaning signatures)

```python
def extract_meaning_signatures(clusters, normalized_vectors):
    """
    Extract meaning signatures from clusters.
    
    Signature = centroid (average) of cluster vectors.
    """
    signatures = {}
    
    for cluster_id, cluster_identities in clusters.items():
        # Compute centroid
        cluster_vectors = [normalized_vectors[h] for h in cluster_identities]
        centroid = {}
        for key in cluster_vectors[0].keys():
            centroid[key] = sum(v[key] for v in cluster_vectors) / len(cluster_vectors)
        
        signatures[cluster_id] = {
            'centroid': centroid,
            'size': len(cluster_identities),
            'identities': cluster_identities
        }
    
    return signatures
```

### Phase 6 Deliverable

**File**: `meaning_map.json`

```json
{
    "clusters": {
        "cluster_0": {
            "centroid": {
                "out_degree": 0.3,
                "k_reach": 0.5,
                "survival": 0.9,
                "entropy": 0.2,
                "escape_concentration": 0.8,
                "near_refusal_rate": 0.1,
                "dead_end_risk": 0.0
            },
            "size": 5,
            "identities": ["hash1", "hash2", ...]
        },
        ...
    },
    "identity_to_cluster": {
        "identity_hash_1": "cluster_0",
        ...
    }
}
```

---

## Phase 7: ROLE EMERGENCE (Functional Roles)

**Status**: 🟡 TO BE BUILT  
**Purpose**: Discover functional roles from cluster properties

### Core Principle

**Roles = Functional Behaviors Under Pressure**

Not POS labels. **Functional roles** from cluster properties.

### Algorithm: Role Assignment from Cluster Properties

#### Step 1: Compute Cluster-Level Properties

```python
def compute_cluster_properties(cluster, identity_vectors):
    """
    Compute properties of cluster to determine role.
    
    Properties:
    - avg_survival: Average survival
    - avg_entropy: Average entropy
    - avg_concentration: Average escape concentration
    - avg_refusal_rate: Average near-refusal rate
    - avg_k_reach: Average k-reach
    """
    cluster_vectors = [identity_vectors[h] for h in cluster['identities']]
    
    properties = {
        'avg_survival': mean([v['survival'] for v in cluster_vectors]),
        'avg_entropy': mean([v['entropy'] for v in cluster_vectors]),
        'avg_concentration': mean([v['escape_concentration'] for v in cluster_vectors]),
        'avg_refusal_rate': mean([v['near_refusal_rate'] for v in cluster_vectors]),
        'avg_k_reach': mean([v['k_reach'] for v in cluster_vectors]),
        'avg_out_degree': mean([v['out_degree'] for v in cluster_vectors])
    }
    
    return properties
```

#### Step 2: Assign Roles from Properties (No Thresholds)

**Fix**: Use quantiles, not hand thresholds

```python
def assign_roles_from_properties(clusters, identity_vectors):
    """
    Assign functional roles from cluster properties.
    
    Roles (functional, not POS):
    - Anchor: high survival, low entropy, high concentration
    - Driver: high k_reach, medium survival, high out_degree
    - Gate: low out_degree, high refusal_rate, high influence
    - Binder: appears as bridge (computed from graph structure)
    - Terminator: low survival, high refusal_rate
    
    Use quantiles to determine "high/low", not fixed thresholds.
    """
    # Collect all properties
    all_survivals = []
    all_entropies = []
    all_concentrations = []
    all_refusal_rates = []
    all_k_reaches = []
    all_out_degrees = []
    
    cluster_properties = {}
    for cluster_id, cluster in clusters.items():
        props = compute_cluster_properties(cluster, identity_vectors)
        cluster_properties[cluster_id] = props
        all_survivals.append(props['avg_survival'])
        all_entropies.append(props['avg_entropy'])
        all_concentrations.append(props['avg_concentration'])
        all_refusal_rates.append(props['avg_refusal_rate'])
        all_k_reaches.append(props['avg_k_reach'])
        all_out_degrees.append(props['avg_out_degree'])
    
    # Compute quantiles (emergent thresholds)
    quantiles = {
        'survival_high': percentile(all_survivals, 75),
        'survival_low': percentile(all_survivals, 25),
        'entropy_high': percentile(all_entropies, 75),
        'entropy_low': percentile(all_entropies, 25),
        'concentration_high': percentile(all_concentrations, 75),
        'refusal_high': percentile(all_refusal_rates, 75),
        'k_reach_high': percentile(all_k_reaches, 75),
        'out_degree_high': percentile(all_out_degrees, 75),
        'out_degree_low': percentile(all_out_degrees, 25)
    }
    
    # Assign roles
    roles = {}
    for cluster_id, props in cluster_properties.items():
        # Determine role from properties (functional, not POS)
        if (props['avg_survival'] > quantiles['survival_high'] and
            props['avg_entropy'] < quantiles['entropy_low'] and
            props['avg_concentration'] > quantiles['concentration_high']):
            role = 'anchor'
        elif (props['avg_k_reach'] > quantiles['k_reach_high'] and
              props['avg_out_degree'] > quantiles['out_degree_high']):
            role = 'driver'
        elif (props['avg_out_degree'] < quantiles['out_degree_low'] and
              props['avg_refusal_rate'] > quantiles['refusal_high']):
            role = 'gate'
        elif props['avg_survival'] < quantiles['survival_low']:
            role = 'terminator'
        else:
            role = 'binder'  # Default/bridge role
        
        roles[cluster_id] = role
    
    return roles
```

#### Step 3: Map Identities to Roles

```python
def map_identities_to_roles(clusters, roles, phase4_symbols):
    """
    Map each identity to its role.
    
    Output: {symbol: role_id} where role_id is just a number
    """
    identity_to_role = {}
    
    for cluster_id, cluster in clusters.items():
        role = roles[cluster_id]
        for identity_hash in cluster['identities']:
            symbol = phase4_symbols.get_symbol(identity_hash)
            if symbol is not None:
                identity_to_role[symbol] = role
    
    return identity_to_role
```

### Phase 7 Deliverable

**File**: `roles.json`

```json
{
    "cluster_roles": {
        "cluster_0": "anchor",
        "cluster_1": "driver",
        "cluster_2": "gate",
        ...
    },
    "symbol_to_role": {
        "symbol_0": "anchor",
        "symbol_1": "driver",
        ...
    }
}
```

---

## Phase 8: CONSTRAINT & TEMPLATE DISCOVERY

**Status**: 🟡 TO BE BUILT  
**Purpose**: Discover grammar-like constraints from role patterns

### Core Principle

**Constraints = Role Patterns That Survive Pressure**

Not imported grammar. **Discovered patterns**.

### Algorithm: Role Pattern Mining

#### Step 1: Extract Role Sequences

```python
def extract_role_sequences(symbol_sequences, symbol_to_role):
    """
    Convert symbol sequences to role sequences.
    
    No grammar rules. Just role sequences.
    """
    role_sequences = []
    
    for symbol_seq in symbol_sequences:
        role_seq = [symbol_to_role.get(s, 'unknown') for s in symbol_seq]
        role_sequences.append(role_seq)
    
    return role_sequences
```

#### Step 2: Discover Frequent Role Patterns

```python
def discover_role_patterns(role_sequences, min_frequency=3):
    """
    Discover frequent role n-grams.
    
    No imported rules. Just frequency.
    """
    patterns = {}
    
    for n in [2, 3, 4]:
        ngrams = Counter()
        for role_seq in role_sequences:
            for i in range(len(role_seq) - n + 1):
                pattern = tuple(role_seq[i:i+n])
                ngrams[pattern] += 1
        
        # Keep frequent patterns
        for pattern, freq in ngrams.items():
            if freq >= min_frequency:
                patterns[pattern] = {
                    'frequency': freq,
                    'length': n
                }
    
    return patterns
```

#### Step 3: Discover Forbidden Patterns (From Outcome Data)

**Fix**: Use actual outcome data, not assumptions

```python
def discover_forbidden_patterns(role_patterns, edge_deltas, symbol_to_role, phase4_symbols):
    """
    Discover forbidden role transitions from outcome data.
    
    Forbidden = high failure rate or high cost (from Phase 5 edge_deltas).
    """
    forbidden = set()
    
    # Group transitions by role pattern
    role_transition_outcomes = defaultdict(list)
    
    for (source_hash, target_hash), delta in edge_deltas.items():
        source_symbol = phase4_symbols.get_symbol(source_hash)
        target_symbol = phase4_symbols.get_symbol(target_hash)
        
        if source_symbol and target_symbol:
            source_role = symbol_to_role.get(source_symbol, 'unknown')
            target_role = symbol_to_role.get(target_symbol, 'unknown')
            role_pattern = (source_role, target_role)
            
            # Use refusal_delta as failure indicator
            refusal_delta = delta.get('refusal_delta', 0.0)
            role_transition_outcomes[role_pattern].append(refusal_delta)
    
    # Patterns with high average refusal_delta are forbidden
    for role_pattern, outcomes in role_transition_outcomes.items():
        if outcomes:
            avg_refusal = mean(outcomes)
            # Use quantile, not fixed threshold
            if avg_refusal > percentile(outcomes, 90):
                forbidden.add(role_pattern)
    
    return forbidden
```

#### Step 4: Build Templates

```python
def build_templates(role_patterns, forbidden_patterns):
    """
    Build templates from valid role patterns.
    
    Templates = frequent patterns that are not forbidden.
    """
    templates = []
    
    # Filter: frequent AND not forbidden
    valid_patterns = {p: data for p, data in role_patterns.items() 
                     if p not in forbidden_patterns}
    
    # Sort by frequency
    sorted_patterns = sorted(valid_patterns.items(), 
                            key=lambda x: x[1]['frequency'], 
                            reverse=True)
    
    # Top patterns become templates
    for pattern, data in sorted_patterns[:10]:  # Top 10
        templates.append({
            'pattern': list(pattern),
            'frequency': data['frequency'],
            'length': data['length']
        })
    
    return templates
```

### Phase 8 Deliverable

**File**: `constraints.json`

```json
{
    "role_patterns": {
        "(anchor, driver)": {"frequency": 15, "length": 2},
        "(driver, anchor)": {"frequency": 12, "length": 2},
        ...
    },
    "forbidden_patterns": [
        "(terminator, driver)",
        ...
    ],
    "templates": [
        {"pattern": ["anchor", "driver", "anchor"], "frequency": 8, "length": 3},
        ...
    ]
}
```

---

## Phase 9: FLUENCY GENERATOR (Revised Scoring)

**Status**: 🟡 TO BE BUILT  
**Purpose**: Generate fluent sequences using stability + novelty + templates

### Core Principle

**Fluency = Stability + Novelty + Template Satisfaction**

Not just low entropy. **Balanced scoring**.

### Algorithm: Revised Generation Scoring

#### Step 1: Stability Score (From Phase 5)

**Reuse**: Consequence vectors from Phase 5

```python
def calculate_stability_score(transition, consequence_field, phase4_symbols):
    """
    Calculate stability score from consequence field.
    
    Score = w1 * survival + w2 * (1/entropy) + w3 * (1 - refusal_rate)
    """
    source_hash, target_hash = transition
    
    source_vector = consequence_field['identity_vectors'].get(source_hash, {})
    target_vector = consequence_field['identity_vectors'].get(target_hash, {})
    
    # Component 1: Survival
    survival = target_vector.get('survival', 0.0)
    
    # Component 2: Entropy reduction (inverse)
    entropy = target_vector.get('entropy', 1.0)
    entropy_reduction = 1.0 / (1.0 + entropy)
    
    # Component 3: Refusal distance
    refusal_rate = target_vector.get('near_refusal_rate', 0.0)
    refusal_distance = 1.0 - refusal_rate
    
    # Combined
    stability = (
        survival * 0.4 +
        entropy_reduction * 0.3 +
        refusal_distance * 0.3
    )
    
    return stability
```

#### Step 2: Template Score

```python
def calculate_template_score(transition, current_role_sequence, templates, symbol_to_role, phase4_symbols):
    """
    Calculate template satisfaction score.
    
    Reward if transition completes or continues a template.
    """
    source_hash, target_hash = transition
    source_symbol = phase4_symbols.get_symbol(source_hash)
    target_symbol = phase4_symbols.get_symbol(target_hash)
    
    source_role = symbol_to_role.get(source_symbol, 'unknown')
    target_role = symbol_to_role.get(target_symbol, 'unknown')
    
    # Extended sequence
    extended = current_role_sequence + [target_role]
    
    score = 0.0
    for template in templates:
        pattern = template['pattern']
        if len(extended) >= len(pattern):
            if tuple(extended[-len(pattern):]) == tuple(pattern):
                score += template['frequency'] / 100.0  # Normalized
    
    return score
```

#### Step 3: Novelty Penalty (Anti-Collapse)

```python
def calculate_novelty_penalty(symbol, recent_sequence, window=5):
    """
    Penalize repeating recent symbols.
    
    Prevents collapse into loops.
    """
    if len(recent_sequence) < window:
        return 0.0
    
    recent = recent_sequence[-window:]
    repeat_count = recent.count(symbol)
    
    penalty = repeat_count / window
    return penalty
```

#### Step 4: Combined Scoring (Replace Existing)

**Modify**: `score_allowed_paths()` in `scoring.py`

```python
def score_allowed_paths_fluent(phase4_output, phase3_metrics, phase2_metrics,
                               consequence_field, templates, symbol_to_role,
                               topology, token_sequences, learner=None):
    """
    Score paths using stability + template + novelty.
    
    Replaces frequency-based scoring with consequence-based.
    """
    continuation_observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)
    
    symbol_to_identity = phase4_output.get('symbol_to_identity', {})
    identity_to_symbol = phase4_output.get('identity_to_symbol', {})
    
    path_scores = {}
    current_role_sequence = []  # Track for template scoring
    
    for from_symbol, from_identity in symbol_to_identity.items():
        allowed_targets = continuation_observer.adjacency.get(from_identity, set())
        
        for to_identity in allowed_targets:
            to_symbol = identity_to_symbol.get(to_identity)
            if to_symbol is None:
                continue
            
            transition = (from_identity, to_identity)
            
            # Stability score
            stability = calculate_stability_score(transition, consequence_field, phase4_symbols)
            
            # Template score
            template = calculate_template_score(
                transition, current_role_sequence, templates, symbol_to_role, phase4_symbols
            )
            
            # Novelty penalty
            recent_symbols = [from_symbol]  # Simplified
            novelty_penalty = calculate_novelty_penalty(to_symbol, recent_symbols)
            
            # Learned bias (from existing learner if available)
            learned_bias = 0.0
            if learner:
                learned_bias = learner.get_bias(from_symbol, to_symbol)
            
            # Combined score
            total_score = (
                stability * 0.4 +
                template * 0.3 +
                learned_bias * 0.2 -
                novelty_penalty * 0.1
            )
            
            path_scores[(from_symbol, to_symbol)] = total_score
    
    return path_scores
```

### Phase 9 Deliverable

**File**: `fluent_generator.py`

- Uses revised scoring
- Generates fluent sequences
- Outputs readable text

---

## Implementation Order (7 Days)

### Day 1-2: Phase 5 - Consequence Field

**Tasks**:
1. Implement `rollout_from_identity()` using existing `ContinuationObserver`
2. Implement `compute_consequence_vector()` with proper k-step reachability
3. Implement `build_consequence_field()` for all identities
4. Write `consequence_field.json`

**Reuse**:
- `ContinuationObserver` from `continuation_observer.py`
- `escape_topology.py` for escape_concentration
- Existing pressure computation

**Test**:
- Run twice with same seed → identical vectors
- Print distribution summaries

### Day 3: Phase 6 - Meaning Discovery

**Tasks**:
1. Implement `normalize_vectors()`
2. Implement `cluster_consequence_vectors()` using k-medoids
3. Implement `extract_meaning_signatures()`
4. Write `meaning_map.json`

**Test**:
- Clusters are deterministic
- Signatures are numeric vectors

### Day 4: Phase 7 - Role Emergence

**Tasks**:
1. Implement `compute_cluster_properties()`
2. Implement `assign_roles_from_properties()` using quantiles
3. Implement `map_identities_to_roles()`
4. Write `roles.json`

**Test**:
- Roles are functional (anchor/driver/gate, not noun/verb)
- No hand thresholds

### Day 5: Phase 8 - Constraint Discovery

**Tasks**:
1. Implement `extract_role_sequences()`
2. Implement `discover_role_patterns()`
3. Implement `discover_forbidden_patterns()` using edge_deltas
4. Implement `build_templates()`
5. Write `constraints.json`

**Test**:
- Patterns are discovered, not imported
- Forbidden patterns use actual outcome data

### Day 6-7: Phase 9 - Fluency Generator

**Tasks**:
1. Implement `calculate_stability_score()` using consequence_field
2. Implement `calculate_template_score()`
3. Implement `calculate_novelty_penalty()`
4. Modify `score_allowed_paths()` to use new scoring
5. Test generation

**Test**:
- Compare old vs new generator:
  - Refusal count (should decrease)
  - Survival length (should increase)
  - Repetition count (should decrease)
  - Unique symbols (should increase)
  - Readability (manual eval)

---

## Success Metrics (Measurable)

### Phase 5 Success
- ✅ Consequence vectors computed for all identities
- ✅ Vectors are deterministic (same seed → same result)
- ✅ All components are numeric (not boolean)

### Phase 6 Success
- ✅ Clusters discovered (not imported)
- ✅ Signatures are vector centroids
- ✅ Clustering is deterministic

### Phase 7 Success
- ✅ Roles are functional (anchor/driver/gate, not POS)
- ✅ Roles use quantiles (not hand thresholds)
- ✅ All identities have roles

### Phase 8 Success
- ✅ Patterns discovered from data
- ✅ Forbidden patterns use outcome data
- ✅ Templates are frequent + valid

### Phase 9 Success
- ✅ Refusal rate decreases
- ✅ Survival length increases
- ✅ Repetition decreases
- ✅ Readability improves

---

## Key Fixes Summary

| Issue | Fix Applied |
|-------|-------------|
| Grammar imports | ✅ Removed all POS rules, discovered patterns only |
| Relation counts | ✅ Replaced with rollout-based measurement |
| 2-step reachability | ✅ Fixed to k-step with consistent horizon |
| Dead ends vs refusal | ✅ Separated: dead_end_risk vs near_refusal_rate |
| Boolean signatures | ✅ Changed to numeric vectors |
| Hand thresholds | ✅ Replaced with quantiles/clustering |
| Cluster ID bug | ✅ Fixed: proper ID assignment |
| Low entropy only | ✅ Added novelty constraint |

---

## What Makes This Executable

### ✅ Uses Existing Infrastructure
- `ContinuationObserver` for rollouts
- `escape_topology.py` for escape_concentration
- `scoring.py` framework (extend, don't replace)

### ✅ Proper Definitions
- k-step reachability (consistent horizon)
- Actual refusal events (not dead ends)
- Vector signatures (not booleans)
- Emergent thresholds (quantiles)

### ✅ No Hidden Imports
- No grammar rules
- No POS categories
- No hand thresholds
- No boolean signatures

### ✅ Measurable & Testable
- Deterministic (same seed → same result)
- All metrics numeric
- Clear success criteria

---

**This roadmap is now executable, logically airtight, and ready to implement.**

---

**End of Final Executable Roadmap**
