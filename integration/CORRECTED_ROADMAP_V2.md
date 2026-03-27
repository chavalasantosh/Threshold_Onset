# Corrected Roadmap V2: Pure First-Principles
## No Hidden Imports, No Silent Cheating

**Date**: 2025-01-13  
**Status**: 🎯 CORRECTED (Based on Critical Feedback)  
**Foundation**: Phases 0-4 (FROZEN)

---

## Critical Corrections Applied

### ❌ What Was Wrong

1. **"Meaning Discovery" was actually Role Discovery** - Confusing labels
2. **Imported POS rules** - "Noun appears after determiners" = imported knowledge
3. **Text → Tokens assumption** - Violates Phase 0 discipline
4. **Topology-only measurement** - Not real meaning
5. **Node-only meaning** - Meaning is on transitions/templates
6. **Hand-picked thresholds** - Not emergent
7. **Boolean signatures** - Too lossy
8. **Fluency = low entropy only** - Needs novelty constraint

### ✅ What's Fixed

1. **Explicit Consequence Layer** - Outcome/cost tracking
2. **Counterfactual Measurement** - Real meaning deltas
3. **Transition-based Meaning** - Not node-only
4. **Explicit Traversal Policy** - Defined interaction
5. **Vector Signatures** - Not booleans
6. **Emergent Thresholds** - Data-driven
7. **Novelty Constraint** - Prevents collapse

---

## The Corrected Chain

```
Input Stream → Action Events → Residue → Segmentation → Identity → Relation → Symbol
                                                                                    ↓
                                                                            Consequence Layer
                                                                                    ↓
                                                                            Role Induction
                                                                                    ↓
                                                                            Constraint Discovery
                                                                                    ↓
                                                                            Template Discovery
                                                                                    ↓
                                                                            Generation (fluent relative to corpus)
```

---

## Phase 5: CONSEQUENCE LAYER (REVISED)

**Status**: 🟡 TO BE BUILT  
**Purpose**: Attach outcome signals to transitions without importing semantics

### Core Principle

**Consequence = Outcome Distribution Under Interaction**

Not topology. Not static counts. **Measurable outcomes** from interaction.

### Algorithm: Consequence Rollout Measurement

#### Step 1: Define Explicit Traversal Policy

**Input**: Phase 3 relations, Phase 4 symbols

**Process**: Define how system traverses graph for measurement

```python
def define_traversal_policy(phase3_relations, phase4_symbols):
    """
    Define explicit traversal policy for consequence measurement.
    
    Policy:
    - Start from given identity
    - Choose next edge that maximizes continuation
    - Avoid refusal (self-transitions forbidden)
    - Log outcomes at each step
    - Stop on refusal, dead-end, or max length
    """
    def traverse_from(identity_hash, max_steps=50):
        """
        Traverse from identity_hash following policy.
        
        Returns:
        - survival_length: How many steps before stop
        - refusal_occurred: Did refusal happen?
        - pressure_accumulated: Total pressure
        - entropy_trajectory: Entropy at each step
        - path_taken: Sequence of identities
        """
        path = [identity_hash]
        pressure = 0.0
        entropy_values = []
        refusal_occurred = False
        
        current = identity_hash
        for step in range(max_steps):
            # Get allowed next identities
            allowed = phase3_relations.get_outgoing(current)
            
            if not allowed:
                # Dead-end
                break
            
            # Choose next: maximize continuation options
            # Score each option by its future continuation count
            scores = {}
            for relation in allowed:
                target = relation['target']
                target_futures = len(phase3_relations.get_outgoing(target))
                scores[target] = target_futures
            
            if not scores:
                break
            
            # Select best (or random if tied)
            best_score = max(scores.values())
            candidates = [t for t, s in scores.items() if s == best_score]
            next_identity = candidates[0] if len(candidates) == 1 else random.choice(candidates)
            
            # Check for refusal (self-transition attempt)
            if next_identity == current:
                refusal_occurred = True
                break
            
            # Update
            path.append(next_identity)
            current = next_identity
            
            # Measure entropy (branching uncertainty)
            current_options = len(phase3_relations.get_outgoing(current))
            entropy = calculate_entropy(current_options)
            entropy_values.append(entropy)
            
            # Measure pressure (inverse of options)
            pressure += 1.0 / max(current_options, 1)
        
        return {
            'survival_length': len(path) - 1,
            'refusal_occurred': refusal_occurred,
            'pressure_accumulated': pressure,
            'entropy_trajectory': entropy_values,
            'path_taken': path
        }
    
    return traverse_from
```

#### Step 2: Measure Contextual Consequence

**Process**: Run rollouts from each identity/transition in different contexts

```python
def measure_contextual_consequence(identity_hash, context, traverse_fn, num_probes=100):
    """
    Measure consequence distribution for identity in context.
    
    Context = set of identities that appeared before
    
    Returns:
    - C(identity | context) = distribution over outcomes
    """
    outcomes = {
        'survival_lengths': [],
        'refusal_rates': [],
        'pressure_values': [],
        'entropy_values': []
    }
    
    for _ in range(num_probes):
        # Run rollout
        result = traverse_fn(identity_hash)
        
        outcomes['survival_lengths'].append(result['survival_length'])
        outcomes['refusal_rates'].append(1.0 if result['refusal_occurred'] else 0.0)
        outcomes['pressure_values'].append(result['pressure_accumulated'])
        if result['entropy_trajectory']:
            outcomes['entropy_values'].append(result['entropy_trajectory'][-1])
    
    # Compute distribution statistics
    return {
        'expected_survival': mean(outcomes['survival_lengths']),
        'survival_variance': variance(outcomes['survival_lengths']),
        'refusal_probability': mean(outcomes['refusal_rates']),
        'expected_pressure': mean(outcomes['pressure_values']),
        'pressure_variance': variance(outcomes['pressure_values']),
        'expected_entropy': mean(outcomes['entropy_values']) if outcomes['entropy_values'] else 0.0,
        'entropy_variance': variance(outcomes['entropy_values']) if outcomes['entropy_values'] else 0.0
    }
```

#### Step 3: Calculate Counterfactual Deltas

**Process**: Measure meaning as change in consequence

```python
def calculate_counterfactual_delta(transition, context, phase3_relations, traverse_fn):
    """
    Calculate meaning as counterfactual delta.
    
    M(transition | context) = C(after transition | context) - C(before | context)
    
    Meaning = how transition changes future outcomes
    """
    source, target = transition
    
    # Measure consequence before (from source)
    consequence_before = measure_contextual_consequence(
        source, context, traverse_fn
    )
    
    # Measure consequence after (from target)
    consequence_after = measure_contextual_consequence(
        target, context, traverse_fn
    )
    
    # Calculate delta
    delta = {
        'survival_delta': consequence_after['expected_survival'] - consequence_before['expected_survival'],
        'refusal_delta': consequence_after['refusal_probability'] - consequence_before['refusal_probability'],
        'pressure_delta': consequence_after['expected_pressure'] - consequence_before['expected_pressure'],
        'entropy_delta': consequence_after['expected_entropy'] - consequence_before['expected_entropy']
    }
    
    return delta
```

#### Step 4: Build Transition Outcome Table

**Output**: Complete outcome table for all transitions

```python
def build_transition_outcome_table(phase3_relations, phase4_symbols, traverse_fn):
    """
    Build outcome table for all allowed transitions.
    
    For each edge (s→t):
    - count: How often it appears
    - contexts: What contexts it appears in
    - outcome: Consequence distribution
    - stability: Variance across runs
    """
    outcome_table = {}
    
    # Get all transitions
    for source_hash in phase3_relations.get_all_identities():
        outgoing = phase3_relations.get_outgoing(source_hash)
        
        for relation in outgoing:
            target_hash = relation['target']
            transition = (source_hash, target_hash)
            
            # Measure in multiple contexts
            contexts = generate_contexts(source_hash, phase3_relations)  # Different context sets
            
            transition_outcomes = []
            for context in contexts:
                delta = calculate_counterfactual_delta(
                    transition, context, phase3_relations, traverse_fn
                )
                transition_outcomes.append(delta)
            
            # Aggregate
            outcome_table[transition] = {
                'count': len(transition_outcomes),
                'contexts': contexts,
                'mean_delta': calculate_mean_delta(transition_outcomes),
                'variance': calculate_variance(transition_outcomes),
                'stability': 1.0 / (1.0 + calculate_variance(transition_outcomes))
            }
    
    return outcome_table
```

### Phase 5 Output

- **Transition outcome table**: All edges with consequence distributions
- **Contextual consequence**: C(identity | context) for each identity
- **Counterfactual deltas**: M(transition | context) for each transition
- **Pressure fields**: Pressure distribution over contexts

---

## Phase 6: ROLE INDUCTION (REVISED - Not "Meaning")

**Status**: 🟡 TO BE BUILT  
**Purpose**: Discover behavioral roles from consequence patterns

### Core Principle

**Roles = Equivalence Classes of Behavior Under Pressure**

Not "meaning". Not labels. **Behavioral signatures**.

### Algorithm: Data-Driven Role Discovery

#### Step 1: Build Feature Vectors (No Hand Thresholds)

**Input**: Phase 5 outcome table, Phase 3 relations

**Process**: Extract features for each identity

```python
def build_behavioral_features(identity_hash, outcome_table, phase3_relations):
    """
    Build feature vector from behavioral data.
    
    Features (all data-driven, no thresholds):
    - out_degree: Number of outgoing relations
    - in_degree: Number of incoming relations
    - relation_type_entropy: Diversity of relation types
    - reciprocal_ratio: How many relations are bidirectional
    - cycle_participation: Does it participate in cycles?
    - betweenness: Connectivity measure
    - outcome_gain: Average survival delta from transitions TO this identity
    - outcome_loss: Average survival delta from transitions FROM this identity
    - context_diversity: How many different contexts it appears in
    - pressure_sensitivity: Variance of pressure across contexts
    """
    features = {}
    
    # Graph features
    outgoing = phase3_relations.get_outgoing(identity_hash)
    incoming = phase3_relations.get_incoming(identity_hash)
    
    features['out_degree'] = len(outgoing)
    features['in_degree'] = len(incoming)
    
    # Relation type entropy
    relation_types = [r['type'] for r in outgoing + incoming]
    features['relation_type_entropy'] = calculate_entropy(relation_types)
    
    # Reciprocal ratio
    reciprocal_count = 0
    for out_rel in outgoing:
        target = out_rel['target']
        if phase3_relations.has_relation(target, identity_hash):
            reciprocal_count += 1
    features['reciprocal_ratio'] = reciprocal_count / max(len(outgoing), 1)
    
    # Cycle participation
    features['cycle_participation'] = check_cycle_participation(identity_hash, phase3_relations)
    
    # Betweenness (simplified)
    features['betweenness'] = calculate_betweenness(identity_hash, phase3_relations)
    
    # Outcome features from Phase 5
    transitions_to = [(s, identity_hash) for s in incoming_sources]
    transitions_from = [(identity_hash, t) for t in outgoing_targets]
    
    outcome_gains = [outcome_table.get(t, {}).get('mean_delta', {}).get('survival_delta', 0.0) 
                     for t in transitions_to]
    outcome_losses = [outcome_table.get(t, {}).get('mean_delta', {}).get('survival_delta', 0.0) 
                      for t in transitions_from]
    
    features['outcome_gain'] = mean(outcome_gains) if outcome_gains else 0.0
    features['outcome_loss'] = mean(outcome_losses) if outcome_losses else 0.0
    
    # Context diversity
    contexts = set()
    for transition in transitions_to + transitions_from:
        if transition in outcome_table:
            contexts.update(outcome_table[transition]['contexts'])
    features['context_diversity'] = len(contexts)
    
    # Pressure sensitivity
    pressure_values = []
    for transition in transitions_to + transitions_from:
        if transition in outcome_table:
            pressure_values.append(outcome_table[transition]['mean_delta'].get('pressure_delta', 0.0))
    features['pressure_sensitivity'] = variance(pressure_values) if pressure_values else 0.0
    
    return features
```

#### Step 2: Cluster by Feature Similarity (Emergent Thresholds)

**Process**: Cluster identities with similar behavioral features

```python
def cluster_roles(phase2_identities, outcome_table, phase3_relations):
    """
    Cluster identities into roles using feature similarity.
    
    No hand thresholds. Clustering is data-driven.
    """
    # Build feature vectors for all identities
    feature_vectors = {}
    for identity_hash in phase2_identities:
        features = build_behavioral_features(identity_hash, outcome_table, phase3_relations)
        feature_vectors[identity_hash] = features
    
    # Normalize features
    normalized = normalize_features(feature_vectors)
    
    # Cluster using distance-based method (no ML, pure algorithm)
    # Use percentile-based similarity threshold
    similarity_threshold = calculate_percentile_threshold(normalized, percentile=75)
    
    # Cluster
    clusters = []
    processed = set()
    
    for identity_hash, features in normalized.items():
        if identity_hash in processed:
            continue
        
        # Find similar identities
        cluster = [identity_hash]
        for other_hash, other_features in normalized.items():
            if other_hash == identity_hash or other_hash in processed:
                continue
            
            # Calculate similarity (cosine or euclidean)
            similarity = calculate_similarity(features, other_features)
            if similarity > similarity_threshold:
                cluster.append(other_hash)
                processed.add(other_hash)
        
        if len(cluster) > 1:
            clusters.append({
                'identities': cluster,
                'role_id': len(clusters),  # Just an ID, no label
                'common_features': calculate_average_features(cluster, normalized)
            })
        processed.add(identity_hash)
    
    return clusters
```

#### Step 3: Assign Roles

**Output**: Identity → Role ID (no human labels)

```python
def assign_roles(clusters, phase4_symbols):
    """
    Assign role IDs to symbols.
    
    Output: Symbol → Role ID (just a number, no "noun"/"verb")
    """
    role_assignments = {}
    
    for cluster in clusters:
        role_id = cluster['role_id']
        for identity_hash in cluster['identities']:
            symbol = phase4_symbols.get_symbol(identity_hash)
            if symbol is not None:
                role_assignments[symbol] = role_id
    
    return role_assignments
```

### Phase 6 Output

- **Role clusters**: Groups of identities with similar behavior
- **Role assignments**: Symbol → Role ID (number, not label)
- **Behavioral signatures**: Feature vectors for each role
- **No human labels**: Just role_0, role_1, role_2, etc.

---

## Phase 7: CONSTRAINT & TEMPLATE DISCOVERY (REVISED)

**Status**: 🟡 TO BE BUILT  
**Purpose**: Discover grammar-like constraints from role patterns (no imported rules)

### Core Principle

**Constraints = Patterns That Survive Pressure**

Not imported grammar rules. **Discovered patterns** from role sequences.

### Algorithm: Role-Based Pattern Discovery

#### Step 1: Extract Role Sequences

**Input**: Phase 6 role assignments, symbol sequences

**Process**: Convert symbol sequences to role sequences

```python
def extract_role_sequences(symbol_sequences, role_assignments):
    """
    Convert symbol sequences to role sequences.
    
    Example:
    symbols: [A, B, C]
    roles: {A: 0, B: 1, C: 0}
    role_sequence: [0, 1, 0]
    """
    role_sequences = []
    
    for symbol_seq in symbol_sequences:
        role_seq = [role_assignments.get(s, -1) for s in symbol_seq]
        role_sequences.append(role_seq)
    
    return role_sequences
```

#### Step 2: Discover Frequent Role Patterns

**Process**: Find n-grams of roles that appear frequently

```python
def discover_role_patterns(role_sequences, min_frequency=3):
    """
    Discover frequent role n-grams (patterns).
    
    No imported rules. Just frequency-based discovery.
    """
    patterns = {}
    
    # Extract n-grams (2, 3, 4)
    for n in [2, 3, 4]:
        ngrams = {}
        for role_seq in role_sequences:
            for i in range(len(role_seq) - n + 1):
                pattern = tuple(role_seq[i:i+n])
                if pattern not in ngrams:
                    ngrams[pattern] = 0
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

#### Step 3: Discover Forbidden Patterns

**Process**: Find role transitions that lead to high failure/cost

```python
def discover_forbidden_patterns(role_patterns, outcome_table, role_assignments, phase3_relations):
    """
    Discover forbidden role transitions from outcome data.
    
    Forbidden = high failure rate or high cost
    """
    forbidden = set()
    
    # Check each role transition
    for role_pattern in role_patterns.keys():
        if len(role_pattern) == 2:  # Pair transitions
            role_a, role_b = role_pattern
            
            # Find all symbol transitions that match this role pattern
            matching_transitions = []
            for transition, outcome in outcome_table.items():
                source, target = transition
                source_role = role_assignments.get(phase4_symbols.get_symbol(source), -1)
                target_role = role_assignments.get(phase4_symbols.get_symbol(target), -1)
                
                if source_role == role_a and target_role == role_b:
                    matching_transitions.append((transition, outcome))
            
            # Check failure rate
            if matching_transitions:
                failure_rates = [outcome.get('mean_delta', {}).get('refusal_delta', 0.0) 
                               for _, outcome in matching_transitions]
                avg_failure = mean(failure_rates)
                
                # High failure = forbidden (emergent threshold)
                if avg_failure > calculate_percentile(failure_rates, 90):
                    forbidden.add(role_pattern)
    
    return forbidden
```

#### Step 4: Build Templates

**Process**: Discover stable slot patterns

```python
def build_templates(role_patterns, forbidden_patterns):
    """
    Build templates from role patterns.
    
    Templates = stable patterns that survive across contexts
    """
    templates = []
    
    # Filter patterns: frequent AND not forbidden
    valid_patterns = {p: data for p, data in role_patterns.items() 
                     if p not in forbidden_patterns}
    
    # Group by length
    for length in [2, 3, 4]:
        length_patterns = {p: data for p, data in valid_patterns.items() 
                          if data['length'] == length}
        
        # Sort by frequency
        sorted_patterns = sorted(length_patterns.items(), 
                                key=lambda x: x[1]['frequency'], 
                                reverse=True)
        
        # Top patterns become templates
        for pattern, data in sorted_patterns[:10]:  # Top 10
            templates.append({
                'pattern': pattern,
                'frequency': data['frequency'],
                'slots': list(pattern)  # Role slots
            })
    
    return templates
```

### Phase 7 Output

- **Role patterns**: Frequent n-grams of roles
- **Forbidden patterns**: High-failure role transitions
- **Templates**: Stable slot patterns
- **No grammar rules**: Just discovered constraints

---

## Phase 8: GENERATION (REVISED)

**Status**: 🟡 TO BE BUILT  
**Purpose**: Generate fluent sequences using constraints + stability + novelty

### Core Principle

**Generation = Constraint Satisfaction + Stability + Anti-Collapse**

Not just low entropy. **Stability + Novelty**.

### Algorithm: Constraint-Based Generation

#### Step 1: Stability Scoring (Revised)

**Process**: Score transitions using Phase 5 outcomes

```python
def calculate_stability_score(transition, outcome_table, current_context):
    """
    Calculate stability score from outcome table.
    
    Score = future_stability + continuation_entropy_reduction + refusal_distance
    """
    if transition not in outcome_table:
        return 0.0
    
    outcome = outcome_table[transition]
    delta = outcome.get('mean_delta', {})
    
    # Future stability
    future_stability = outcome.get('stability', 0.0)
    
    # Continuation entropy reduction (inverse of entropy delta)
    entropy_delta = delta.get('entropy_delta', 0.0)
    entropy_reduction = 1.0 / (1.0 + abs(entropy_delta))
    
    # Refusal distance (inverse of refusal delta)
    refusal_delta = delta.get('refusal_delta', 0.0)
    refusal_distance = 1.0 - abs(refusal_delta)
    
    # Combined
    stability_score = (
        future_stability * 0.4 +
        entropy_reduction * 0.3 +
        refusal_distance * 0.3
    )
    
    return stability_score
```

#### Step 2: Novelty Constraint (Anti-Collapse)

**Process**: Penalize repeating recent patterns

```python
def calculate_novelty_penalty(symbol, recent_sequence, window=5):
    """
    Calculate novelty penalty for symbol.
    
    Penalize if symbol repeats in recent window.
    """
    if len(recent_sequence) < window:
        return 0.0
    
    recent = recent_sequence[-window:]
    repeat_count = recent.count(symbol)
    
    # Penalty increases with repeats
    penalty = repeat_count / window
    
    return penalty
```

#### Step 3: Template Satisfaction

**Process**: Reward transitions that match templates

```python
def calculate_template_score(transition, current_role_sequence, templates, role_assignments, phase4_symbols):
    """
    Calculate template satisfaction score.
    
    Reward if transition completes or continues a template pattern.
    """
    source, target = transition
    source_role = role_assignments.get(phase4_symbols.get_symbol(source), -1)
    target_role = role_assignments.get(phase4_symbols.get_symbol(target), -1)
    
    # Check if current sequence + new transition matches any template
    extended_sequence = current_role_sequence + [target_role]
    
    score = 0.0
    for template in templates:
        pattern = template['pattern']
        if len(extended_sequence) >= len(pattern):
            # Check if last N roles match template
            if tuple(extended_sequence[-len(pattern):]) == pattern:
                score += template['frequency'] / 100.0  # Normalized
    
    return score
```

#### Step 4: Generate Sequence

**Process**: Select transitions that maximize combined score

```python
def generate_fluent_sequence(start_symbol, length, outcome_table, templates, role_assignments, 
                            phase3_relations, phase4_symbols):
    """
    Generate fluent sequence using all constraints.
    
    Score = stability + template_satisfaction - novelty_penalty
    """
    sequence = [start_symbol]
    role_sequence = [role_assignments.get(start_symbol, -1)]
    
    current_symbol = start_symbol
    
    for _ in range(length - 1):
        # Get allowed transitions
        current_identity = phase4_symbols.get_identity(current_symbol)
        allowed = phase3_relations.get_outgoing(current_identity)
        allowed_symbols = [phase4_symbols.get_symbol(r['target']) for r in allowed]
        
        # Score each candidate
        scores = {}
        for symbol in allowed_symbols:
            if symbol is None:
                continue
            
            transition = (current_identity, phase4_symbols.get_identity(symbol))
            
            # Stability score
            stability = calculate_stability_score(transition, outcome_table, role_sequence)
            
            # Template score
            template = calculate_template_score(transition, role_sequence, templates, 
                                               role_assignments, phase4_symbols)
            
            # Novelty penalty
            novelty_penalty = calculate_novelty_penalty(symbol, sequence)
            
            # Combined score
            total_score = stability + template - novelty_penalty
            scores[symbol] = total_score
        
        # Select best
        if scores:
            best_symbol = max(scores.items(), key=lambda x: x[1])[0]
            sequence.append(best_symbol)
            role_sequence.append(role_assignments.get(best_symbol, -1))
            current_symbol = best_symbol
        else:
            break
    
    # Convert to text
    text = phase4_symbols.symbols_to_text(sequence)
    return text
```

### Phase 8 Output

- **Fluent sequences**: Quality, readable output
- **Constraint satisfaction**: Follows discovered templates
- **Stability**: Low refusal, high continuation
- **Novelty**: Prevents collapse into loops

---

## Success Criteria (Revised)

### Phase 5 Success
- ✅ Transition outcome table complete
- ✅ Contextual consequence measured
- ✅ Counterfactual deltas calculated
- ✅ No hand thresholds

### Phase 6 Success
- ✅ Roles discovered from behavior
- ✅ No human labels (just role IDs)
- ✅ Emergent clustering
- ✅ Feature vectors data-driven

### Phase 7 Success
- ✅ Role patterns discovered
- ✅ Forbidden patterns identified
- ✅ Templates built
- ✅ No imported grammar rules

### Phase 8 Success
- ✅ Fluent sequences generated
- ✅ Stability + novelty balanced
- ✅ Template satisfaction
- ✅ Readability achieved

---

## Key Fixes Applied

1. ✅ **Consequence Layer Added** - Explicit outcome tracking
2. ✅ **Counterfactual Measurement** - Real meaning deltas
3. ✅ **Transition-based** - Meaning on edges, not just nodes
4. ✅ **Explicit Traversal Policy** - Defined interaction
5. ✅ **Vector Signatures** - Not booleans
6. ✅ **Emergent Thresholds** - Data-driven, not handpicked
7. ✅ **Novelty Constraint** - Prevents collapse
8. ✅ **No POS Rules** - Discovered patterns only
9. ✅ **No Human Labels** - Just IDs and numbers
10. ✅ **Input Stream** - Not "Text → Tokens"

---

## Implementation Order

1. **Phase 5**: Consequence Layer (rollout measurement)
2. **Phase 6**: Role Induction (behavioral clustering)
3. **Phase 7**: Constraint Discovery (role patterns)
4. **Phase 8**: Generation (stability + novelty)

---

**All from first principles. No hidden imports. No silent cheating.**

---

**End of Corrected Roadmap V2**
