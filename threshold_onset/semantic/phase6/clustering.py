"""
Clustering Algorithms for Meaning Discovery

Enterprise-grade k-medoids clustering with stability-based cluster selection.

CORRECTED: Stability-based cluster count selection (not hand-chosen).
"""

import logging
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from threshold_onset.semantic.common.utils import (
    calculate_similarity,
    mean,
    variance
)

logger = logging.getLogger('threshold_onset.semantic.phase6')


def calculate_distance(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """
    Calculate Euclidean distance between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Euclidean distance
    """
    # Get common keys
    keys = set(vec1.keys()) & set(vec2.keys())
    
    if not keys:
        return float('inf')
    
    squared_diff = sum((vec1[k] - vec2[k]) ** 2 for k in keys)
    return math.sqrt(squared_diff)


def k_medoids_pam(
    vectors: List[Dict[str, float]],
    k: int,
    max_iterations: int = 100
) -> Dict[int, List[int]]:
    """
    k-Medoids clustering using PAM (Partitioning Around Medoids) algorithm.
    
    Deterministic algorithm (not ML training).
    
    Args:
        vectors: List of normalized vectors
        k: Number of clusters
        max_iterations: Maximum iterations
        
    Returns:
        Dictionary mapping cluster_id -> list of vector indices
    """
    n = len(vectors)
    if n == 0:
        return {}
    
    if k >= n:
        # Each vector is its own cluster
        return {i: [i] for i in range(n)}
    
    if k < 1:
        k = 1
    
    # Initialize: select k random medoids (deterministic: first k)
    medoid_indices = list(range(k))
    medoids = [vectors[i] for i in medoid_indices]
    
    # Assign vectors to nearest medoid
    clusters = defaultdict(list)
    for i, vector in enumerate(vectors):
        distances = [calculate_distance(vector, medoid) for medoid in medoids]
        nearest_medoid = min(range(k), key=lambda j: distances[j])
        clusters[nearest_medoid].append(i)
    
    # PAM algorithm: swap medoids to minimize total cost
    for iteration in range(max_iterations):
        improved = False
        
        for cluster_id in range(k):
            if not clusters[cluster_id]:
                continue
            
            current_medoid_idx = medoid_indices[cluster_id]
            current_cost = sum(
                calculate_distance(vectors[i], vectors[current_medoid_idx])
                for i in clusters[cluster_id]
            )
            
            # Try swapping with each non-medoid in cluster
            best_swap = None
            best_cost = current_cost
            
            for candidate_idx in clusters[cluster_id]:
                if candidate_idx == current_medoid_idx:
                    continue
                
                # Calculate cost with candidate as medoid
                candidate_cost = sum(
                    calculate_distance(vectors[i], vectors[candidate_idx])
                    for i in clusters[cluster_id]
                )
                
                if candidate_cost < best_cost:
                    best_cost = candidate_cost
                    best_swap = candidate_idx
            
            # Perform swap if improvement
            if best_swap is not None:
                medoid_indices[cluster_id] = best_swap
                medoids[cluster_id] = vectors[best_swap]
                improved = True
        
        if not improved:
            break
        
        # Reassign all vectors to nearest medoid
        clusters = defaultdict(list)
        for i, vector in enumerate(vectors):
            distances = [calculate_distance(vector, medoid) for medoid in medoids]
            nearest_medoid = min(range(k), key=lambda j: distances[j])
            clusters[nearest_medoid].append(i)
    
    logger.debug(f"k-medoids PAM completed in {iteration + 1} iterations")
    
    return dict(clusters)


def compute_intra_cluster_distance(
    cluster_indices: List[int],
    vectors: List[Dict[str, float]]
) -> float:
    """
    Compute average intra-cluster distance.
    
    Args:
        cluster_indices: Indices of vectors in cluster
        vectors: All vectors
        
    Returns:
        Average intra-cluster distance
    """
    if len(cluster_indices) < 2:
        return 0.0
    
    distances = []
    for i in range(len(cluster_indices)):
        for j in range(i + 1, len(cluster_indices)):
            dist = calculate_distance(
                vectors[cluster_indices[i]],
                vectors[cluster_indices[j]]
            )
            distances.append(dist)
    
    return mean(distances) if distances else 0.0


def compute_cluster_stability(
    vectors: List[Dict[str, float]],
    k: int,
    num_bootstrap: int = 10,
    seed: Optional[int] = None
) -> float:
    """
    Compute cluster assignment stability under bootstrap.
    
    CORRECTED: Stability-based cluster selection.
    
    Args:
        vectors: List of vectors
        k: Number of clusters
        num_bootstrap: Number of bootstrap samples
        seed: Random seed (for deterministic bootstrap)
        
    Returns:
        Stability score [0.0, 1.0] (higher = more stable)
    """
    if len(vectors) < k:
        return 0.0
    
    import random
    if seed is not None:
        random.seed(seed)
    
    n = len(vectors)
    assignments_list = []
    
    for _ in range(num_bootstrap):
        # Bootstrap sample (with replacement)
        sample_indices = [random.randint(0, n - 1) for _ in range(n)]
        sample_vectors = [vectors[i] for i in sample_indices]
        
        # Cluster sample
        clusters = k_medoids_pam(sample_vectors, k)
        
        # Create assignment vector (which cluster each original vector belongs to)
        # Map sample indices back to original indices
        assignment = {}
        for cluster_id, cluster_indices in clusters.items():
            for sample_idx in cluster_indices:
                original_idx = sample_indices[sample_idx]
                assignment[original_idx] = cluster_id
        
        assignments_list.append(assignment)
    
    # Compute stability: how often do pairs end up in same cluster?
    if len(assignments_list) < 2:
        return 0.0
    
    stability_scores = []
    for i in range(len(assignments_list)):
        for j in range(i + 1, len(assignments_list)):
            assign1 = assignments_list[i]
            assign2 = assignments_list[j]
            
            # Count agreements (same cluster assignment)
            agreements = 0
            total = 0
            
            for idx in range(n):
                if idx in assign1 and idx in assign2:
                    if assign1[idx] == assign2[idx]:
                        agreements += 1
                    total += 1
            
            if total > 0:
                stability_scores.append(agreements / total)
    
    return mean(stability_scores) if stability_scores else 0.0


def select_optimal_k(
    vectors: List[Dict[str, float]],
    k_min: int = 2,
    k_max: Optional[int] = None,
    seed: Optional[int] = None
) -> int:
    """
    Select optimal k using stability vs complexity tradeoff.
    
    CORRECTED: Stability-based selection (not hand-chosen).
    
    Args:
        vectors: List of vectors to cluster
        k_min: Minimum k to consider
        k_max: Maximum k to consider (default: sqrt(n))
        seed: Random seed
        
    Returns:
        Optimal k value
    """
    n = len(vectors)
    if n < 2:
        return 1
    
    if k_max is None:
        k_max = min(int(math.sqrt(n)), n // 2)
    
    k_min = max(2, min(k_min, n))
    k_max = max(k_min, min(k_max, n))
    
    logger.info(f"Selecting optimal k from [{k_min}, {k_max}] for {n} vectors")
    
    best_k = k_min
    best_score = -1.0
    
    for k in range(k_min, k_max + 1):
        # Cluster with k
        clusters = k_medoids_pam(vectors, k)
        
        # Compute average intra-cluster distance
        intra_distances = []
        for cluster_indices in clusters.values():
            if len(cluster_indices) > 1:
                intra_dist = compute_intra_cluster_distance(cluster_indices, vectors)
                intra_distances.append(intra_dist)
        
        avg_intra_distance = mean(intra_distances) if intra_distances else float('inf')
        
        # Compute stability
        stability = compute_cluster_stability(vectors, k, num_bootstrap=5, seed=seed)
        
        # Score: stability / (1 + complexity)
        # Higher stability, lower complexity (fewer clusters) = better
        complexity_penalty = k / n  # Normalize by number of vectors
        score = stability / (1.0 + complexity_penalty)
        
        logger.debug(
            f"k={k}: stability={stability:.3f}, "
            f"avg_intra_distance={avg_intra_distance:.3f}, score={score:.3f}"
        )
        
        if score > best_score:
            best_score = score
            best_k = k
    
    logger.info(f"Selected optimal k={best_k} with score={best_score:.3f}")
    return best_k


def cluster_consequence_vectors(
    normalized_vectors: Dict[str, Dict[str, float]],
    num_clusters: Optional[int] = None,
    seed: Optional[int] = None
) -> Dict[str, List[str]]:
    """
    Cluster consequence vectors using k-medoids.
    
    CORRECTED: Uses stability-based cluster selection if num_clusters not specified.
    
    Args:
        normalized_vectors: Dictionary mapping identity_hash -> normalized vector
        num_clusters: Number of clusters (None = auto-select by stability)
        seed: Random seed for determinism
        
    Returns:
        Dictionary mapping cluster_id -> list of identity_hashes
    """
    if not normalized_vectors:
        return {}
    
    # Convert to list for clustering
    identity_list = list(normalized_vectors.keys())
    vector_list = [normalized_vectors[h] for h in identity_list]
    
    # Determine number of clusters
    if num_clusters is None:
        # CORRECTED: Stability-based selection
        num_clusters = select_optimal_k(vector_list, seed=seed)
    else:
        num_clusters = max(2, min(num_clusters, len(identity_list)))
    
    logger.info(f"Clustering {len(identity_list)} vectors into {num_clusters} clusters")
    
    # k-medoids clustering
    clusters = k_medoids_pam(vector_list, num_clusters)
    
    # Map back to identity hashes
    result = {}
    for cluster_id, vector_indices in clusters.items():
        identity_hashes = [identity_list[i] for i in vector_indices]
        result[f"cluster_{cluster_id}"] = identity_hashes
    
    return result
