"""
Metrics Computer

Computes validation metrics from system outputs.
"""

import logging
from typing import Dict, Any, List, Optional
import math

logger = logging.getLogger(__name__)


class MetricsComputer:
    """Computes validation metrics."""
    
    @staticmethod
    def compute_phase5_metrics(
        consequence_field: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Phase 5 metrics.
        
        Args:
            consequence_field: ConsequenceField data
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "num_identities": 0,
            "num_vectors": 0,
            "avg_entropy": 0.0,
            "max_entropy": 0.0,
            "min_entropy": float('inf'),
            "entropy_variance": 0.0,
            "num_edge_deltas": 0
        }
        
        if not consequence_field:
            return metrics
        
        identity_vectors = consequence_field.get('identity_vectors', {})
        edge_deltas = consequence_field.get('edge_deltas', {})
        
        metrics["num_identities"] = len(identity_vectors)
        metrics["num_vectors"] = len(identity_vectors)
        metrics["num_edge_deltas"] = len(edge_deltas)
        
        # Compute entropy statistics
        entropies = []
        for identity_hash, vector in identity_vectors.items():
            if isinstance(vector, dict):
                entropy = vector.get('entropy', 0.0)
            elif isinstance(vector, list):
                # Compute entropy from vector
                entropy = MetricsComputer._compute_entropy_from_vector(vector)
            else:
                entropy = 0.0
            
            entropies.append(entropy)
        
        if entropies:
            metrics["avg_entropy"] = sum(entropies) / len(entropies)
            metrics["max_entropy"] = max(entropies)
            metrics["min_entropy"] = min(entropies)
            metrics["entropy_variance"] = MetricsComputer._compute_variance(entropies)
        
        return metrics
    
    @staticmethod
    def compute_phase6_metrics(
        meaning_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Phase 6 metrics.
        
        Args:
            meaning_map: MeaningMap data
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "num_clusters": 0,
            "avg_cluster_size": 0.0,
            "max_cluster_size": 0,
            "min_cluster_size": float('inf'),
            "cluster_stability_scores": [],
            "avg_stability": 0.0
        }
        
        if not meaning_map:
            return metrics
        
        clusters = meaning_map.get('clusters', {})
        metrics["num_clusters"] = len(clusters)
        
        cluster_sizes = []
        stability_scores = []
        
        for cluster_id, cluster_data in clusters.items():
            if isinstance(cluster_data, dict):
                size = cluster_data.get('size', 0)
                stability = cluster_data.get('stability', 0.0)
            else:
                # Try to infer from structure
                size = len(cluster_data) if isinstance(cluster_data, (list, dict)) else 1
                stability = 0.0
            
            cluster_sizes.append(size)
            stability_scores.append(stability)
        
        if cluster_sizes:
            metrics["avg_cluster_size"] = sum(cluster_sizes) / len(cluster_sizes)
            metrics["max_cluster_size"] = max(cluster_sizes)
            metrics["min_cluster_size"] = min(cluster_sizes)
        
        metrics["cluster_stability_scores"] = stability_scores
        if stability_scores:
            metrics["avg_stability"] = sum(stability_scores) / len(stability_scores)
        
        return metrics
    
    @staticmethod
    def compute_phase7_metrics(
        roles: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Phase 7 metrics.
        
        Args:
            roles: RoleMap data
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "num_role_assignments": 0,
            "role_distribution": {},
            "role_variance": 0.0,
            "num_binders": 0,
            "num_unclassified": 0
        }
        
        if not roles:
            return metrics
        
        cluster_roles = roles.get('cluster_roles', {})
        metrics["num_role_assignments"] = len(cluster_roles)
        
        # Count role distribution
        role_counts = {}
        for cluster_id, role in cluster_roles.items():
            role_counts[role] = role_counts.get(role, 0) + 1
        
        metrics["role_distribution"] = role_counts
        
        # Compute variance (entropy of role distribution)
        if role_counts:
            total = sum(role_counts.values())
            probabilities = [count / total for count in role_counts.values()]
            metrics["role_variance"] = MetricsComputer._compute_entropy(probabilities)
        
        metrics["num_binders"] = role_counts.get('binder', 0)
        metrics["num_unclassified"] = role_counts.get('unclassified', 0)
        
        return metrics
    
    @staticmethod
    def compute_phase8_metrics(
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Phase 8 metrics.
        
        Args:
            constraints: ConstraintMap data
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "num_patterns": 0,
            "num_forbidden": 0,
            "num_templates": 0,
            "avg_pattern_frequency": 0.0,
            "avg_template_score": 0.0,
            "constraint_rigidity_scores": []
        }
        
        if not constraints:
            return metrics
        
        patterns = constraints.get('role_patterns', {})
        forbidden = constraints.get('forbidden_patterns', [])
        templates = constraints.get('templates', {})
        
        metrics["num_patterns"] = len(patterns)
        metrics["num_forbidden"] = len(forbidden)
        metrics["num_templates"] = len(templates)
        
        # Compute pattern frequency statistics
        frequencies = []
        if isinstance(patterns, dict):
            for pattern_id, pattern_data in patterns.items():
                if isinstance(pattern_data, dict):
                    freq = pattern_data.get('frequency', 0)
                else:
                    freq = 1
                frequencies.append(freq)
        elif isinstance(patterns, list):
            # Handle case where patterns is a list
            for pattern_data in patterns:
                if isinstance(pattern_data, dict):
                    freq = pattern_data.get('frequency', 0)
                else:
                    freq = 1
                frequencies.append(freq)
        
        if frequencies:
            metrics["avg_pattern_frequency"] = sum(frequencies) / len(frequencies)
        
        # Compute template scores
        template_scores = []
        if isinstance(templates, dict):
            for template_id, template_data in templates.items():
                if isinstance(template_data, dict):
                    score = template_data.get('score', 0.0)
                else:
                    score = 0.0
                template_scores.append(score)
        elif isinstance(templates, list):
            # Handle case where templates is a list
            for template_data in templates:
                if isinstance(template_data, dict):
                    score = template_data.get('score', 0.0)
                else:
                    score = 0.0
                template_scores.append(score)
        
        if template_scores:
            metrics["avg_template_score"] = sum(template_scores) / len(template_scores)
        
        # Rigidity scores (simplified: based on frequency)
        metrics["constraint_rigidity_scores"] = [
            min(1.0, freq / 10.0) for freq in frequencies
        ]
        
        return metrics
    
    @staticmethod
    def compute_phase9_metrics(
        fluency_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Phase 9 metrics.
        
        Args:
            fluency_output: Fluency generation output
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "generated_length": 0,
            "fluency_gate_passed": False,
            "stability_score": 0.0,
            "entropy_at_gate": 0.0,
            "refusal_triggered": False
        }
        
        if not fluency_output:
            return metrics
        
        sequence = fluency_output.get('sequence', [])
        metrics["generated_length"] = len(sequence)
        
        gate_decision = fluency_output.get('gate_decision', 'UNKNOWN')
        metrics["fluency_gate_passed"] = gate_decision == 'PASS'
        metrics["refusal_triggered"] = gate_decision == 'REFUSE'
        
        metrics["stability_score"] = fluency_output.get('stability_score', 0.0)
        metrics["entropy_at_gate"] = fluency_output.get('entropy', 0.0)
        
        return metrics
    
    @staticmethod
    def _compute_entropy(probabilities: List[float]) -> float:
        """Compute Shannon entropy."""
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    @staticmethod
    def _compute_entropy_from_vector(vector: List[float]) -> float:
        """Compute entropy from a vector of values."""
        if not vector:
            return 0.0
        
        # Normalize to probabilities
        total = sum(abs(v) for v in vector)
        if total == 0:
            return 0.0
        
        probabilities = [abs(v) / total for v in vector]
        return MetricsComputer._compute_entropy(probabilities)
    
    @staticmethod
    def _compute_variance(values: List[float]) -> float:
        """Compute variance."""
        if not values:
            return 0.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance
