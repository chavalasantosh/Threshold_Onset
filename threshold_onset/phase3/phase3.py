"""
THRESHOLD_ONSET — Phase 3: RELATION

Relation without naming.
Graph structures without symbolic labels.
Interactions without meaning.
Dependencies without interpretation.
Influence measurement without semantics.

Phase 3 operates as separate layer from Phase 0, Phase 1, and Phase 2.
Reads Phase 0, Phase 1, and Phase 2 output only. Does not modify them.
"""

from collections import deque
import os
from concurrent.futures import ThreadPoolExecutor

# FIXED thresholds for Phase 3 gate (non-adaptive)
# These values are external and fixed, not computed from data
MIN_PERSISTENT_RELATIONS = 1
MIN_STABILITY_RATIO = 0.6


def _env_int(name, default, minimum=1):
    raw = os.environ.get(name)
    if not raw:
        return max(minimum, int(default))
    try:
        return max(minimum, int(raw))
    except ValueError:
        return max(minimum, int(default))


def _env_flag(name, default=False):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _phase3_single_run(payload):
    """
    Execute one Phase-3 run payload and extract relation outputs.
    """
    residues, phase1_metrics, phase2_metrics = payload
    from threshold_onset.phase3.relation import extract_relations  # pylint: disable=import-outside-toplevel

    phase3_metrics = phase3(residues, phase1_metrics, phase2_metrics)
    relation_result = extract_relations(phase3_metrics)
    graph_metrics = {
        'node_count': phase3_metrics['node_count'],
        'edge_count': phase3_metrics['edge_count'],
        'graph_nodes': phase3_metrics['graph_nodes'],
        'graph_edges': phase3_metrics['graph_edges']
    }
    return relation_result['relation_hashes'], relation_result['relation_counts'], graph_metrics


def phase3(residues, phase1_metrics, phase2_metrics):
    """
    Phase 3 relation pipeline.
    
    Operates on opaque residues from Phase 0, metrics from Phase 1, and identity metrics from Phase 2.
    Performs relation detection without naming.
    Returns relation metrics only (graph structures, counts, hash pairs).
    
    Args:
        residues: list of opaque residues (floats from Phase 0)
        phase1_metrics: dictionary with Phase 1 structural metrics
        phase2_metrics: dictionary with Phase 2 identity metrics
    
    Returns:
        Dictionary with relation metrics:
        - 'graph_nodes': set of identity hashes (node identifiers, internal only)
        - 'graph_edges': set of tuples (hash_pair) representing edges (internal identifiers only)
        - 'node_count': number of nodes (int)
        - 'edge_count': number of edges (int)
        - 'degree_counts': dict mapping node hash to degree count (int)
        - 'interaction_counts': dict mapping hash pair tuple to interaction count (int)
        - 'interaction_pairs': set of hash pair tuples (internal identifiers only)
        - 'dependency_counts': dict mapping hash pair tuple to dependency count (int)
        - 'dependency_pairs': set of hash pair tuples (internal identifiers only)
        - 'influence_counts': dict mapping hash pair tuple to influence count (int)
        - 'influence_strengths': dict mapping hash pair tuple to raw number (float)
        - 'path_lengths': list of path lengths (raw numbers, int)
    """
    from threshold_onset.phase3.graph import build_graph  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase3.interaction import detect_interactions  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase3.dependency import measure_dependencies  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase3.influence import measure_influence  # pylint: disable=import-outside-toplevel
    
    # Build graph structure
    graph_result = build_graph(phase2_metrics)
    graph_nodes = graph_result['nodes']
    graph_edges = graph_result['edges']
    
    # Detect interactions
    interaction_result = detect_interactions(residues, phase2_metrics)
    interaction_counts = interaction_result['interaction_counts']
    interaction_pairs = interaction_result['interaction_pairs']
    
    # Measure dependencies
    dependency_result = measure_dependencies(residues, phase2_metrics)
    dependency_counts = dependency_result['dependency_counts']
    dependency_pairs = dependency_result['dependency_pairs']
    
    # Measure influence
    influence_result = measure_influence(residues, phase2_metrics)
    influence_counts = influence_result['influence_counts']
    influence_strengths = influence_result['influence_strengths']
    
    # Compute graph metrics
    node_count = len(graph_nodes)
    edge_count = len(graph_edges)
    
    # Compute degree counts
    degree_counts = _compute_degree_counts(graph_nodes, graph_edges)
    
    # Compute path lengths (optional in performance-sensitive runs)
    if _env_flag("PHASE3_SKIP_PATH_LENGTHS", default=False):
        path_lengths = []
    else:
        path_lengths = _compute_path_lengths(graph_nodes, graph_edges)
    
    return {
        'graph_nodes': graph_nodes,
        'graph_edges': graph_edges,
        'node_count': node_count,
        'edge_count': edge_count,
        'degree_counts': degree_counts,
        'interaction_counts': interaction_counts,
        'interaction_pairs': interaction_pairs,
        'dependency_counts': dependency_counts,
        'dependency_pairs': dependency_pairs,
        'influence_counts': influence_counts,
        'influence_strengths': influence_strengths,
        'path_lengths': path_lengths
    }


def _compute_degree_counts(nodes, edges):
    """
    Compute degree counts for each node in graph.
    
    Degree = number of edges connected to node.
    Uses exact hash equality.
    
    Args:
        nodes: set of node hashes (internal identifiers only)
        edges: set of edge tuples (hash pairs, internal identifiers only)
    
    Returns:
        Dictionary mapping node hash to degree count (int)
    """
    degree_counts = {}
    
    # Initialize all nodes with degree 0
    for node in nodes:
        degree_counts[node] = 0
    
    # Count edges for each node
    for edge in edges:
        hash1, hash2 = edge
        # Use exact equality for hash comparison
        if hash1 in nodes:
            degree_counts[hash1] = degree_counts.get(hash1, 0) + 1
        if hash2 in nodes:
            degree_counts[hash2] = degree_counts.get(hash2, 0) + 1
    
    return degree_counts


def _compute_path_lengths(nodes, edges):
    """
    Compute shortest path lengths between nodes using BFS.
    
    Path length = number of edges in path.
    Only computes paths between nodes that are actually connected.
    Uses exact hash equality for node/edge matching.
    
    Args:
        nodes: set of node hashes (internal identifiers only)
        edges: set of edge tuples (hash pairs, internal identifiers only)
    
    Returns:
        List of path lengths (raw numbers, int)
    """
    if len(nodes) < 2:
        return []
    
    # Build adjacency list
    adjacency = {}
    for node in nodes:
        adjacency[node] = []
    
    for edge in edges:
        hash1, hash2 = edge
        # Use exact equality for hash comparison
        if hash1 in nodes and hash2 in nodes:
            adjacency[hash1].append(hash2)
            adjacency[hash2].append(hash1)
    
    # Compute shortest paths using BFS from each node
    path_lengths = []
    node_list = list(nodes)
    
    for start_node in node_list:
        # BFS from start_node
        visited = {start_node}
        queue = deque([(start_node, 0)])  # (node, distance)
        
        while queue:
            current_node, distance = queue.popleft()
            
            # Add path length if we've moved (distance > 0)
            if distance > 0:
                path_lengths.append(distance)
            
            # Explore neighbors
            for neighbor in adjacency[current_node]:
                # Use exact equality for hash comparison
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
    
    return path_lengths


def phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics):
    """
    Phase 3 relation pipeline with multiple runs.
    
    Tests persistence and stability across multiple independent Phase 0 runs.
    Operates on opaque residues from multiple Phase 0 runs, metrics from Phase 1, and identity metrics from Phase 2.
    Performs relation detection without naming.
    Returns relation metrics only (graph structures, counts, hash pairs).
    
    Args:
        residue_sequences: list of residue sequences (each from a separate Phase 0 run)
        phase1_metrics_list: list of Phase 1 metrics (one per run)
        phase2_metrics: Phase 2 metrics from multi-run (aggregated)
    
    Returns:
        Dictionary with relation metrics (if gate passes), or None (if gate fails)
    """
    from threshold_onset.phase3.relation import extract_relations  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase3.persistence import measure_relation_persistence  # pylint: disable=import-outside-toplevel
    from threshold_onset.phase3.stability import measure_relation_stability  # pylint: disable=import-outside-toplevel
    
    worker_count = min(
        max(1, _env_int("PHASE3_WORKERS", default=os.cpu_count() or 1)),
        max(1, len(residue_sequences)),
    )

    # Step 1: Run Phase 3 for each run and collect relations
    relation_hashes_per_run = []
    relation_counts_per_run = []
    graph_metrics_per_run = []

    if worker_count > 1 and len(residue_sequences) > 1:
        payloads = [
            (residues, phase1_metrics, phase2_metrics)
            for residues, phase1_metrics in zip(residue_sequences, phase1_metrics_list)
        ]
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            results = list(pool.map(_phase3_single_run, payloads))
        for relation_hashes, relation_counts, graph_metrics in results:
            relation_hashes_per_run.append(relation_hashes)
            relation_counts_per_run.append(relation_counts)
            graph_metrics_per_run.append(graph_metrics)
    else:
        for residues, phase1_metrics in zip(residue_sequences, phase1_metrics_list):
            # Run Phase 3 for this run
            phase3_metrics = phase3(residues, phase1_metrics, phase2_metrics)
            
            # Extract relations from Phase 3 metrics
            relation_result = extract_relations(phase3_metrics)
            relation_hashes_per_run.append(relation_result['relation_hashes'])
            relation_counts_per_run.append(relation_result['relation_counts'])
            
            # Store graph metrics for stability measurement
            graph_metrics_per_run.append({
                'node_count': phase3_metrics['node_count'],
                'edge_count': phase3_metrics['edge_count'],
                'graph_nodes': phase3_metrics['graph_nodes'],
                'graph_edges': phase3_metrics['graph_edges']
            })
    
    # Step 2: Measure relation persistence
    persistence_result = measure_relation_persistence(relation_hashes_per_run)
    persistent_relation_hashes = persistence_result['persistent_relation_hashes']
    persistence_rate = persistence_result['persistence_rate']
    persistent_relations = len(persistent_relation_hashes)
    
    # Step 3: Measure relation stability (ONLY on persistent relations)
    stability_result = measure_relation_stability(
        relation_hashes_per_run,
        relation_counts_per_run,
        graph_metrics_per_run,
        persistent_relation_hashes
    )
    stability_ratio = stability_result['stability_ratio']
    
    # Step 4: Check gate (store values for potential failure message)
    persistent_segments = len(phase2_metrics.get('persistent_segment_hashes', []))
    identity_mappings = len(phase2_metrics.get('identity_mappings', {}))
    gate_passed = _check_phase3_gate(phase2_metrics, persistent_relations, stability_ratio)
    
    if not gate_passed:
        # Gate failed - return None with failure info
        # Store diagnostic info in a way that can be accessed if needed
        # (main.py will handle the output message)
        return None  # Gate failed, refuse execution
    
    # Step 5: Aggregate graph structure (union of all nodes and edges)
    aggregated_nodes = set()
    aggregated_edges = set()
    for graph_metrics in graph_metrics_per_run:
        aggregated_nodes.update(graph_metrics['graph_nodes'])
        aggregated_edges.update(graph_metrics['graph_edges'])
    
    # Aggregate relation counts across all runs
    aggregated_relation_counts = {}
    for relation_counts in relation_counts_per_run:
        for relation_hash, count in relation_counts.items():
            aggregated_relation_counts[relation_hash] = aggregated_relation_counts.get(relation_hash, 0) + count
    
    # Aggregate all relation hashes
    aggregated_relation_hashes = set()
    for relation_set in relation_hashes_per_run:
        aggregated_relation_hashes.update(relation_set)
    
    # Compute aggregated path lengths (from first run's graph)
    if _env_flag("PHASE3_SKIP_PATH_LENGTHS", default=False):
        path_lengths = []
    elif len(graph_metrics_per_run) > 0:
        first_graph = graph_metrics_per_run[0]
        path_lengths = _compute_path_lengths(first_graph['graph_nodes'], first_graph['graph_edges'])
    else:
        path_lengths = []
    
    return {
        'relation_hashes': aggregated_relation_hashes,
        'relation_counts': aggregated_relation_counts,
        'persistent_relation_hashes': persistent_relation_hashes,
        'persistence_rate': persistence_rate,
        'stable_relation_hashes': stability_result['stable_relation_hashes'],
        'stability_ratio': stability_ratio,
        'edge_density_variance': stability_result['edge_density_variance'],
        'common_edges_ratio': stability_result['common_edges_ratio'],
        'graph_nodes': aggregated_nodes,
        'graph_edges': aggregated_edges,
        'node_count': len(aggregated_nodes),
        'edge_count': len(aggregated_edges),
        'path_lengths': path_lengths
    }


def _check_phase3_gate(phase2_metrics, persistent_relations, stability_ratio):
    """
    Check if Phase 3 gate criteria are met.
    
    Phase 3 must refuse execution unless ALL three criteria are met:
    1. Phase 2 produced persistent identities
    2. Persistent relations exist (≥ MIN_PERSISTENT_RELATIONS)
    3. Stability threshold met (stability_ratio ≥ MIN_STABILITY_RATIO)
    
    Args:
        phase2_metrics: dictionary with Phase 2 identity metrics
        persistent_relations: number of persistent relations (int)
        stability_ratio: stability ratio (float, 0.0 to 1.0)
    
    Returns:
        True if gate passes, False if gate fails
    """
    # Criterion 1: Phase 2 produced persistent identities
    persistent_segments = len(phase2_metrics.get('persistent_segment_hashes', []))
    identity_mappings = len(phase2_metrics.get('identity_mappings', {}))
    has_persistent_identities = persistent_segments > 0 or identity_mappings > 0
    
    # Criterion 2: Persistent relations exist
    has_persistent_relations = persistent_relations >= MIN_PERSISTENT_RELATIONS
    
    # Criterion 3: Stability threshold met
    meets_stability_threshold = stability_ratio >= MIN_STABILITY_RATIO
    
    # All three criteria must be met
    return has_persistent_identities and has_persistent_relations and meets_stability_threshold
