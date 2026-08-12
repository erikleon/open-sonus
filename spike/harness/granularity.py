"""Infer a receiver's real seek resolution from where it started reading.

A receiver may accept a seek target it cannot honour. Sonos accepts a millisecond target,
returns success, and starts on the whole second below it. So the resolution has to be read
from behaviour rather than from the return value, and this module does the reading.
"""

from __future__ import annotations

from dataclasses import dataclass

# Coarsest first. The report names the coarsest step consistent with the data, because
# that is the weakest actuator the evidence rules out, and a control loop has to be
# designed against the weakest one. Binary fractions are included because a receiver
# working in power-of-two subdivisions lands on 0.125 rather than on 0.1.
#
# The list stops at 1.0 on purpose. A grid coarser than a second cannot be told apart
# from a one-second grid unless the targets are spread to reveal it, and it would not
# change any decision: both are far outside any sync budget worth publishing.
CANDIDATE_QUANTA_S = (
    1.0, 0.5, 0.25, 0.2, 0.125, 0.1, 0.0625, 0.05, 0.025, 0.02, 0.01, 0.005, 0.002, 0.001,
)


@dataclass(frozen=True)
class SeekObservation:
    requested_s: float
    observed_s: float

    @property
    def error_s(self) -> float:
        return self.observed_s - self.requested_s


@dataclass(frozen=True)
class GranularityReport:
    quantum_s: float | None
    behaviour: str
    worst_error_ms: float
    observations: tuple[SeekObservation, ...]

    def finer_than(self, budget_ms: float) -> bool:
        """Whether this actuator can express a correction inside the sync budget."""
        if self.quantum_s is None:
            return True
        return self.quantum_s * 1000.0 <= budget_ms

    def summary(self, budget_ms: float | None = None) -> str:
        step = "finer than 1 ms" if self.quantum_s is None else f"{self.quantum_s * 1000:g} ms"
        text = (
            f"seek quantum {step}, behaviour {self.behaviour}, "
            f"worst error {self.worst_error_ms:+.1f} ms"
        )
        if budget_ms is not None:
            verdict = "inside" if self.finer_than(budget_ms) else "COARSER THAN"
            text += f" — {verdict} a {budget_ms:g} ms budget"
        return text


def _divides_all(quantum: float, values: list[float], tolerance_s: float) -> bool:
    for value in values:
        steps = round(value / quantum)
        if abs(value - steps * quantum) > tolerance_s:
            return False
    return True


def infer_quantum(
    observations: list[SeekObservation], tolerance_s: float = 1e-6
) -> float | None:
    """Coarsest step size that every observed position lands on.

    Returns None when no candidate divides the data, which means the receiver honoured the
    request more finely than the candidate list resolves.
    """
    if not observations:
        raise ValueError("need at least one observation to infer a quantum")
    values = [o.observed_s for o in observations]
    for quantum in CANDIDATE_QUANTA_S:
        if _divides_all(quantum, values, tolerance_s):
            return quantum
    return None


def classify_behaviour(
    observations: list[SeekObservation], tolerance_s: float = 1e-6
) -> str:
    """How the receiver disposes of the part of the request it cannot honour."""
    errors = [o.error_s for o in observations]
    if all(abs(e) <= tolerance_s for e in errors):
        return "exact"
    if all(e <= tolerance_s for e in errors):
        return "truncate"
    if all(e >= -tolerance_s for e in errors):
        return "round up"
    return "round to nearest"


def analyse(
    observations: list[SeekObservation], tolerance_s: float = 1e-6
) -> GranularityReport:
    worst = max((o.error_s for o in observations), key=abs, default=0.0)
    return GranularityReport(
        quantum_s=infer_quantum(observations, tolerance_s),
        behaviour=classify_behaviour(observations, tolerance_s),
        worst_error_ms=worst * 1000.0,
        observations=tuple(observations),
    )
