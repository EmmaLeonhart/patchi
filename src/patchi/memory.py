"""LT-3 — memory as recursion, and an operational definition of "artificial time".

Pygmalion: "memory is a recursion function … input alters the values of memory
and the combination of values input and memory generates an output that becomes
[the next state]" (the flip-flop analogy), and memory is a tuple
``<TemporalLogic, SpatialLogic>``. The notebook titles itself "artificial time"
but never pins the term down.

**The operational definition adopted here:** *artificial time is the discrete
index of the memory recursion* — the count of update steps the system has taken.
It is the system's own internal clock, advanced only by ``step`` and entirely
**decoupled from wall-clock time**. This makes "artificial time" a concrete,
measurable quantity (``Memory.time``) instead of a slogan, and it is exactly the
``TemporalLogic`` half of the memory tuple: an ordering over experiential states
``m_0, m_1, m_2, …`` where ``before(m_i, m_j) ⟺ i < j``.

The recursion itself is a leaky accumulator ``m_{t+1} = decay · m_t + input_t``
(a reservoir-style state). This is the minimum honest realisation; the spatial
half (vector-algebra gating via the blocks) plugs in later.

See ``literature/REVIEW.md`` §1/§5 and ``todo.md`` LT-3.
"""

from __future__ import annotations

from typing import Iterable, List

import numpy as np


class Memory:
    """A recurrent memory cell with an artificial-time clock.

    ``m_{t+1} = decay · m_t + input_t``; ``time`` is the number of steps taken.
    """

    def __init__(self, dim: int, decay: float = 0.5, gate=None) -> None:
        if dim <= 0:
            raise ValueError("dim must be positive")
        if not 0.0 <= decay <= 1.0:
            raise ValueError("decay must be in [0, 1]")
        if gate is not None and getattr(gate, "dim", dim) != dim:
            raise ValueError(f"gate dim {gate.dim} must match memory dim {dim}")
        self._dim = dim
        self._decay = float(decay)
        self._gate = gate
        self._state = np.zeros(dim, dtype=float)
        self._t = 0

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def decay(self) -> float:
        return self._decay

    @property
    def spatial_gate(self):
        """The SpatialLogic component: the NeuralBlock gating each input (or None)."""
        return self._gate

    def memory_tuple(self):
        """Pygmalion's ``<TemporalLogic, SpatialLogic>``: ``(artificial time, gate)``."""
        return (self._t, self._gate)

    @property
    def time(self) -> int:
        """Artificial time: the number of recursion steps taken so far."""
        return self._t

    @property
    def state(self) -> np.ndarray:
        return self._state.copy()

    def step(self, input_vec: Iterable[float]) -> np.ndarray:
        """Advance one tick of artificial time; return the new state.

        The recurrence is ``m_{t+1} = decay·m_t + gate(input_t)``: SpatialLogic
        (the gate block) transforms the input via vector algebra before it enters
        the temporal recursion. With no gate this is plain accumulation.
        """
        x = np.asarray(list(input_vec), dtype=float)
        if x.shape != (self._dim,):
            raise ValueError(f"input must have shape ({self._dim},), got {x.shape}")
        if self._gate is not None:
            x = np.asarray(self._gate.apply(x), dtype=float)
        self._state = self._decay * self._state + x
        self._t += 1
        return self._state.copy()

    def run(self, sequence: Iterable[Iterable[float]]) -> List[np.ndarray]:
        """Feed a sequence of inputs; return the state after each step."""
        return [self.step(x) for x in sequence]

    def reset(self) -> None:
        """Return to the initial state and reset artificial time to 0."""
        self._state = np.zeros(self._dim, dtype=float)
        self._t = 0

    @staticmethod
    def before(i: int, j: int) -> bool:
        """TemporalLogic primitive over artificial-time indices: ``i < j``."""
        return i < j
