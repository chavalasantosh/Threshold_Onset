"""
THRESHOLD_ONSET — Phase 0 Action Variants

Structured but meaningless actions for Phase 0.
All actions are Phase 0 compliant: numeric, opaque, no meaning, no labels.

Internal state is allowed as long as:
- It's not named externally
- It's not interpreted
- It's not displayed
- It's mechanical only
"""

import random
import math


class InertiaAction:
    """
    Random with Inertia.
    
    Action(t+1) depends slightly on Action(t).
    Stateful action with carry-over (internal state, no naming).
    """
    def __init__(self):
        self._state = random.random()  # Internal state, not a name
    
    def __call__(self):
        # Weak correlation: new value = 0.7 * old + 0.3 * random
        self._state = 0.7 * self._state + 0.3 * random.random()
        return self._state


class BoundedWalk:
    """
    Bounded Random Walk.
    
    Action drifts within bounds.
    Position is internal state, not named.
    """
    def __init__(self):
        self._position = random.random()
        self._step_size = 0.1  # Fixed, not adaptive
    
    def __call__(self):
        # Random walk with reflection at boundaries
        step = (random.random() - 0.5) * self._step_size
        self._position = max(0.0, min(1.0, self._position + step))
        return self._position


class DecayNoise:
    """
    Decay + Noise.
    
    Action decays with added noise.
    Decay is mechanical, not interpreted.
    """
    def __init__(self):
        self._value = random.random()
        self._decay = 0.95  # Fixed decay rate
    
    def __call__(self):
        # Decay towards random target
        target = random.random()
        self._value = self._decay * self._value + (1 - self._decay) * target
        return self._value


class WeakOscillator:
    """
    Weak Oscillator.
    
    Action oscillates with noise.
    Oscillation is mechanical, not interpreted.
    """
    def __init__(self):
        self._phase = random.random() * 2 * math.pi
        self._frequency = 0.1  # Fixed frequency
        self._amplitude = 0.3  # Fixed amplitude
    
    def __call__(self):
        # Oscillation with noise
        self._phase += self._frequency
        oscillation = 0.5 + self._amplitude * math.sin(self._phase)
        noise = random.random() * 0.2
        return max(0.0, min(1.0, oscillation + noise))


class FiniteAction:
    """
    Finite Action.
    
    Action outputs from a small finite set.
    Discreteness is mechanical, not interpreted.
    No labels, no meaning, just finite outputs.
    
    Phase 0 compliant: discrete but meaningless.
    """
    def __init__(self, finite_set_size=10):
        """
        Args:
            finite_set_size: size of finite output set (default: 10, outputs 0-9)
        """
        self._finite_set_size = finite_set_size
        self._state = random.randint(0, finite_set_size - 1)  # Internal state
    
    def __call__(self):
        # Output from finite set (0 to finite_set_size-1)
        # State transitions are mechanical, not interpreted
        # Add small random change to state (modulo finite set)
        change = random.randint(-1, 1)  # -1, 0, or +1
        self._state = (self._state + change) % self._finite_set_size
        return float(self._state)  # Return as float for consistency