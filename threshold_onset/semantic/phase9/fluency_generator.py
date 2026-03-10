"""
Fluency Generator

Enterprise-grade fluent text generation using stability + novelty + templates.

CORRECTED: Experience table (not "learner"), prefix-match templates.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

from threshold_onset.semantic.common.exceptions import FluencyGenerationError
from threshold_onset.semantic.common.validators import validate_symbol
from threshold_onset.semantic.config.defaults import (
    DEFAULT_STABILITY_WEIGHT,
    DEFAULT_TEMPLATE_WEIGHT,
    DEFAULT_BIAS_WEIGHT,
    DEFAULT_NOVELTY_WEIGHT,
    DEFAULT_NOVELTY_WINDOW
)
from threshold_onset.semantic.phase9.scoring import (
    calculate_stability_score,
    calculate_novelty_penalty,
    calculate_experience_bias
)

logger = logging.getLogger('threshold_onset.semantic.phase9')


class FluencyGenerator:
    """
    Fluency Generator
    
    Generates fluent sequences by optimizing:
    - Consequence stability
    - Template progression
    - Novelty (anti-loop)
    - Refusal distance
    
    All corrections applied:
    - Experience table (not "learner")
    - Prefix-match template scoring
    - Stability + Novelty + Template balance
    """
    
    def __init__(
        self,
        consequence_field: Any,  # ConsequenceField
        roles: Any,  # RoleMap
        constraints: Any,  # ConstraintMap
        phase3_relations: Dict[str, Any],
        phase4_symbols: Dict[str, Any],
        continuation_observer: Any,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize fluency generator.
        
        Args:
            consequence_field: ConsequenceField from Phase 5
            roles: RoleMap from Phase 7
            constraints: ConstraintMap from Phase 8
            phase3_relations: Phase 3 relation metrics
            phase4_symbols: Phase 4 symbol mappings
            continuation_observer: ContinuationObserver instance
            config: Optional configuration overrides
        """
        self.consequence_field = consequence_field
        self.roles = roles
        self.constraints = constraints
        self.phase3_relations = phase3_relations
        self.phase4_symbols = phase4_symbols
        self.continuation_observer = continuation_observer
        self.config = config or {}
        
        phase9_config = self.config.get('phase9', {})
        self.stability_weight = phase9_config.get('stability_weight', DEFAULT_STABILITY_WEIGHT)
        self.template_weight = phase9_config.get('template_weight', DEFAULT_TEMPLATE_WEIGHT)
        self.bias_weight = phase9_config.get('bias_weight', DEFAULT_BIAS_WEIGHT)
        self.novelty_weight = phase9_config.get('novelty_weight', DEFAULT_NOVELTY_WEIGHT)
        self.novelty_window = phase9_config.get('novelty_window', DEFAULT_NOVELTY_WINDOW)
        
        # Experience table (CORRECTED: not "learner")
        self.experience_table: Dict[Tuple[int, int], float] = {}
        
        # Symbol to identity mapping
        self.symbol_to_identity = phase4_symbols.get('symbol_to_identity', {})
        self.identity_to_symbol = phase4_symbols.get('identity_to_symbol', {})
        
        # Symbol to role mapping
        self.symbol_to_role = roles.get('symbol_to_role', {})
        
        logger.info(
            f"FluencyGenerator initialized: "
            f"weights=({self.stability_weight}, {self.template_weight}, "
            f"{self.bias_weight}, {self.novelty_weight})"
        )
    
    def build_experience_table(
        self,
        edge_deltas: Optional[Dict[Tuple[str, str], Dict[str, float]]] = None
    ) -> None:
        """
        Build experience table from consequence deltas.
        
        CORRECTED: Experience table (not "learner").
        Deterministic update rule, derived from consequence deltas.
        
        Args:
            edge_deltas: Optional edge deltas (defaults to consequence_field.edge_deltas)
        """
        if edge_deltas is None:
            edge_deltas = self.consequence_field.edge_deltas
        
        # Build experience table from edge deltas
        # Positive survival_delta = good experience
        # Negative survival_delta = bad experience
        for (source_hash, target_hash), delta in edge_deltas.items():
            source_symbol = self.identity_to_symbol.get(source_hash)
            target_symbol = self.identity_to_symbol.get(target_hash)
            
            if source_symbol is None or target_symbol is None:
                continue
            
            transition = (source_symbol, target_symbol)
            
            # Use survival_delta as experience signal
            survival_delta = delta.get('survival_delta', 0.0)
            
            # Normalize to [-1, 1] range
            # Positive delta = positive experience
            experience_bias = max(-1.0, min(1.0, survival_delta))
            
            self.experience_table[transition] = experience_bias
        
        logger.info(f"Built experience table with {len(self.experience_table)} entries")
    
    def score_transition(
        self,
        transition: Tuple[int, int],
        current_role_sequence: List[str],
        recent_symbols: List[int]
    ) -> float:
        """
        Score transition using stability + template + novelty + experience.
        
        CORRECTED: Prefix-match template scoring, experience table.
        
        Args:
            transition: (source_symbol, target_symbol) tuple
            current_role_sequence: Current role sequence
            recent_symbols: Recent symbol sequence (for novelty)
            
        Returns:
            Combined score [0.0, 1.0]
        """
        source_symbol, target_symbol = transition
        
        # Get identity hashes
        source_hash = self.symbol_to_identity.get(source_symbol)
        target_hash = self.symbol_to_identity.get(target_symbol)
        
        if source_hash is None or target_hash is None:
            return 0.0
        
        # Component 1: Stability score
        stability = calculate_stability_score(
            (source_hash, target_hash),
            self.consequence_field
        )
        
        # Component 2: Template score (prefix-match)
        target_role = self.symbol_to_role.get(target_symbol, 'unclassified')
        extended_roles = current_role_sequence + [target_role]
        
        template_score = 0.0
        # Use constraint discovery engine's prefix-match scoring
        if isinstance(self.constraints, dict):
            templates = self.constraints.get('templates', [])
            if templates:
                from threshold_onset.semantic.phase8.pattern_miner import compute_prefix_match_score
                for template in templates[:10]:  # Top 10 templates
                    pattern = template.get('pattern', [])
                    score = compute_prefix_match_score(
                        extended_roles,
                        pattern,
                        window=self.novelty_window
                    )
                    if score > 0:
                        # Weight by frequency
                        weighted_score = score * (template.get('frequency', 1) / 100.0)
                        template_score = max(template_score, weighted_score)
        
        # Component 3: Experience bias
        experience_bias = calculate_experience_bias(
            transition,
            self.experience_table
        )
        # Normalize to [0, 1] for scoring
        experience_score = (experience_bias + 1.0) / 2.0
        
        # Component 4: Novelty penalty
        novelty_penalty = calculate_novelty_penalty(
            target_symbol,
            recent_symbols,
            window=self.novelty_window
        )
        
        # Combined score
        total_score = (
            stability * self.stability_weight +
            template_score * self.template_weight +
            experience_score * self.bias_weight -
            novelty_penalty * self.novelty_weight
        )
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, total_score))
    
    def generate(
        self,
        start_symbol: int,
        length: int = 50,
        seed: Optional[int] = None
    ) -> List[int]:
        """
        Generate fluent symbol sequence.
        
        Args:
            start_symbol: Starting symbol ID
            length: Desired sequence length
            seed: Random seed (for deterministic selection)
            
        Returns:
            List of symbol IDs
            
        Raises:
            FluencyGenerationError: If generation fails
        """
        validate_symbol(start_symbol)
        
        if start_symbol not in self.symbol_to_identity:
            raise FluencyGenerationError(
                f"Start symbol {start_symbol} not found in symbol mappings"
            )
        
        # Build experience table if not built
        if not self.experience_table:
            self.build_experience_table()
        
        sequence = [start_symbol]
        current_symbol = start_symbol
        current_role_sequence = []
        
        logger.info(f"Generating sequence of length {length} from symbol {start_symbol}")
        
        for step in range(length - 1):
            # Get current identity
            current_hash = self.symbol_to_identity.get(current_symbol)
            if current_hash is None:
                logger.warning(f"Symbol {current_symbol} has no identity mapping")
                break
            
            # Get allowed transitions
            allowed_targets = self.continuation_observer.adjacency.get(current_hash, set())
            
            if not allowed_targets:
                logger.debug(f"No allowed transitions from {current_symbol}, stopping")
                break
            
            # Score all allowed transitions
            scores = {}
            for target_hash in allowed_targets:
                target_symbol = self.identity_to_symbol.get(target_hash)
                if target_symbol is None:
                    continue
                
                transition = (current_symbol, target_symbol)
                
                # Check if transition is allowed
                if not self.continuation_observer._check_transition_allowed(
                    current_hash, target_hash
                ):
                    continue
                
                # Score transition
                score = self.score_transition(
                    transition,
                    current_role_sequence,
                    sequence[-self.novelty_window:]
                )
                scores[target_symbol] = score
            
            if not scores:
                logger.debug("No valid transitions found, stopping")
                break
            
            # Select best scoring transition
            best_score = max(scores.values())
            candidates = [s for s, sc in scores.items() if sc == best_score]
            
            # Deterministic tie-breaking
            if seed is not None:
                import random
                random.seed(seed + step)
                next_symbol = random.choice(candidates)
            else:
                next_symbol = sorted(candidates)[0]
            
            # Add to sequence
            sequence.append(next_symbol)
            
            # Update role sequence
            next_role = self.symbol_to_role.get(next_symbol, 'unclassified')
            current_role_sequence.append(next_role)
            if len(current_role_sequence) > self.novelty_window:
                current_role_sequence.pop(0)
            
            current_symbol = next_symbol
        
        logger.info(f"Generated sequence of length {len(sequence)}")
        return sequence
    
    def generate_text(
        self,
        start_symbol: int,
        length: int = 50,
        symbol_to_text: Optional[Dict[int, str]] = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Generate fluent text sequence.
        
        Args:
            start_symbol: Starting symbol ID
            length: Desired sequence length
            symbol_to_text: Optional mapping of symbol -> text (for output)
            seed: Random seed
            
        Returns:
            Generated text string
        """
        sequence = self.generate(start_symbol, length, seed)
        
        if symbol_to_text:
            # Convert symbols to text
            text_parts = [symbol_to_text.get(s, f"[{s}]") for s in sequence]
            return ' '.join(text_parts)
        else:
            # Return symbol sequence as string
            return ' '.join(str(s) for s in sequence)
