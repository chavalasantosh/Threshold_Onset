"""
THRESHOLD_ONSET — Corpus Structural Memory (Phase 1)

Corpus-level state accumulation per docs/STABILITY_LAW.md.
Identity stability and edge weights evolve with reinforcement, decay, atomicization.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple

# Default parameters from STABILITY_LAW.md
DEFAULT_REINFORCEMENT = 1.0
DEFAULT_DECAY_RATE = 0.1
DEFAULT_T_ATOMIC = 10.0
DEFAULT_THETA_PRUNE = 0.01
DEFAULT_CORE_DECAY_FACTOR = 0.1
DEFAULT_MAX_IDENTITIES = 100_000
DEFAULT_MAX_EDGES = 500_000


def _edge_key(a: str, b: str) -> Tuple[str, str]:
    """Canonical edge key (undirected)."""
    return (min(a, b), max(a, b))


class CorpusState:
    """
    Corpus-level structural memory.

    Maintains:
    - identity_stability: dict[identity_hash, S]
    - edge_weights: dict[(a,b), W]
    - core_identities: set of identity hashes with S > T_atomic
    """

    def __init__(
        self,
        reinforcement: float = DEFAULT_REINFORCEMENT,
        decay_rate: float = DEFAULT_DECAY_RATE,
        T_atomic: float = DEFAULT_T_ATOMIC,
        theta_prune: float = DEFAULT_THETA_PRUNE,
        core_decay_factor: float = DEFAULT_CORE_DECAY_FACTOR,
        max_identities: int = DEFAULT_MAX_IDENTITIES,
        max_edges: int = DEFAULT_MAX_EDGES,
        prune_interval_docs: int = 10,
    ):
        self.reinforcement = reinforcement
        self.decay_rate = decay_rate
        self.T_atomic = T_atomic
        self.theta_prune = theta_prune
        self.core_decay_factor = core_decay_factor
        self.max_identities = max_identities
        self.max_edges = max_edges
        self.prune_interval_docs = prune_interval_docs

        self.identity_stability: Dict[str, float] = {}
        self.edge_weights: Dict[Tuple[str, str], float] = {}
        self.core_identities: Set[str] = set()
        self.doc_count = 0

    def update(
        self,
        identity_hashes: Set[str],
        edge_pairs: Set[Tuple[str, str]],
    ) -> None:
        """
        Update state for one document.

        Order: reinforce present, decay absent, atomicize, prune (if scheduled).
        """
        # 1. Reinforce present identities
        for h in identity_hashes:
            if h not in self.identity_stability:
                self.identity_stability[h] = self.reinforcement
            else:
                self.identity_stability[h] += self.reinforcement

        # 2. Decay absent identities
        d_core = self.decay_rate * self.core_decay_factor
        for h in list(self.identity_stability.keys()):
            if h not in identity_hashes:
                d = d_core if h in self.core_identities else self.decay_rate
                self.identity_stability[h] *= 1.0 - d

        # 3. Reinforce present edges
        for (a, b) in edge_pairs:
            key = _edge_key(a, b)
            if key not in self.edge_weights:
                self.edge_weights[key] = self.reinforcement
            else:
                self.edge_weights[key] += self.reinforcement

        # 4. Decay absent edges (no core for edges; use same decay)
        for key in list(self.edge_weights.keys()):
            a, b = key
            present = (a, b) in edge_pairs or (b, a) in edge_pairs
            if not present:
                self.edge_weights[key] *= 1.0 - self.decay_rate

        # 5. Atomicize
        for h, s in list(self.identity_stability.items()):
            if s > self.T_atomic:
                self.core_identities.add(h)

        # 6. Prune (if scheduled)
        self.doc_count += 1
        if self.doc_count % self.prune_interval_docs == 0:
            self._prune()

        # 7. Enforce caps
        self._enforce_caps()

    def _prune(self) -> None:
        """Remove low-stability identities and edges."""
        # Prune identities (except core)
        to_remove = [
            h for h, s in self.identity_stability.items()
            if s < self.theta_prune and h not in self.core_identities
        ]
        for h in to_remove:
            del self.identity_stability[h]
            self.core_identities.discard(h)

        # Prune edges
        to_remove_edges = [
            k for k, w in self.edge_weights.items()
            if w < self.theta_prune
        ]
        for k in to_remove_edges:
            del self.edge_weights[k]

    def _enforce_caps(self) -> None:
        """Evict lowest-stability objects when over cap."""
        if len(self.identity_stability) > self.max_identities:
            ranked = sorted(
                self.identity_stability.items(),
                key=lambda x: (x[1], x[0])
            )
            evict = len(self.identity_stability) - self.max_identities
            for h, _ in ranked[:evict]:
                if h not in self.core_identities:
                    del self.identity_stability[h]
                    self.core_identities.discard(h)

        if len(self.edge_weights) > self.max_edges:
            ranked = sorted(
                self.edge_weights.items(),
                key=lambda x: (x[1], x[0])
            )
            evict = len(self.edge_weights) - self.max_edges
            for k, _ in ranked[:evict]:
                del self.edge_weights[k]

    def get_identity_stability(self, identity_hash: str) -> float:
        """Return stability for identity, or 0 if unknown."""
        return self.identity_stability.get(identity_hash, 0.0)

    def get_edge_weight(self, a: str, b: str) -> float:
        """Return weight for edge (a,b), or 0 if unknown."""
        return self.edge_weights.get(_edge_key(a, b), 0.0)

    def is_core(self, identity_hash: str) -> bool:
        """Return True if identity is core."""
        return identity_hash in self.core_identities

    def metrics(self) -> Dict[str, Any]:
        """Return current metrics."""
        return {
            "corpus_identities_count": len(self.identity_stability),
            "corpus_edges_count": len(self.edge_weights),
            "corpus_core_count": len(self.core_identities),
            "corpus_doc_count": self.doc_count,
        }

    def save(self, path: Path) -> None:
        """Persist state to JSON."""
        data = {
            "version": 1,
            "identity_stability": self.identity_stability,
            "edge_weights": {f"{a}|{b}": w for (a, b), w in self.edge_weights.items()},
            "core_identities": list(self.core_identities),
            "doc_count": self.doc_count,
            "params": {
                "reinforcement": self.reinforcement,
                "decay_rate": self.decay_rate,
                "T_atomic": self.T_atomic,
                "theta_prune": self.theta_prune,
            },
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Path, **overrides) -> "CorpusState":
        """Load state from JSON. If file has trailing garbage (Extra data), use first JSON object only."""
        path = Path(path)
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            if "Extra data" in str(e):
                data, _ = json.JSONDecoder().raw_decode(raw)
            else:
                raise

        state = cls(
            reinforcement=overrides.get("reinforcement", data["params"]["reinforcement"]),
            decay_rate=overrides.get("decay_rate", data["params"]["decay_rate"]),
            T_atomic=overrides.get("T_atomic", data["params"]["T_atomic"]),
            theta_prune=overrides.get("theta_prune", data["params"]["theta_prune"]),
        )
        state.identity_stability = data["identity_stability"]
        state.edge_weights = {}
        for k, w in data["edge_weights"].items():
            a, b = k.split("|", 1)
            state.edge_weights[_edge_key(a, b)] = w
        state.core_identities = set(data["core_identities"])
        state.doc_count = data["doc_count"]
        return state
