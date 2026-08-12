"""The inference has to survive the case it was built for: a receiver that reports success
and then does something coarser than it was asked for."""

from __future__ import annotations

import pytest

from spike.harness.granularity import (
    SeekObservation,
    analyse,
    classify_behaviour,
    infer_quantum,
)


def obs(pairs):
    return [SeekObservation(requested, observed) for requested, observed in pairs]


# The five seeks actually measured against a Sonos Play:3 on 2026-08-11.
MEASURED_SONOS = obs(
    [
        (30.0, 30.0),
        (90.5, 90.0),
        (150.25, 150.0),
        (210.125, 210.0),
        (260.75, 260.0),
    ]
)


def test_recovers_one_second_quantum_from_measured_data():
    assert infer_quantum(MEASURED_SONOS) == 1.0


def test_measured_data_is_truncation_not_rounding():
    assert classify_behaviour(MEASURED_SONOS) == "truncate"


def test_measured_actuator_is_outside_a_ten_millisecond_budget():
    report = analyse(MEASURED_SONOS)
    assert not report.finer_than(10.0)
    assert "COARSER THAN" in report.summary(10.0)


def test_worst_error_is_the_largest_magnitude_not_the_last():
    report = analyse(MEASURED_SONOS)
    assert report.worst_error_ms == pytest.approx(-750.0)


def test_exact_receiver_is_read_as_honouring_the_finest_target_offered():
    exact = obs([(30.0, 30.0), (90.5, 90.5), (150.25, 150.25), (210.125, 210.125)])
    assert infer_quantum(exact) == 0.125  # the finest binary fraction the targets contain
    assert classify_behaviour(exact) == "exact"
    # Still outside a 10 ms budget: an exact receiver is only ever shown to be as fine as
    # the targets asked it to be, so the probe cannot credit it with more.
    assert analyse(exact).finer_than(10.0) is False


def test_sub_millisecond_receiver_falls_off_the_candidate_list():
    fine = obs([(30.0004, 30.0004), (90.0007, 90.0007)])
    assert infer_quantum(fine) is None
    assert analyse(fine).finer_than(10.0) is True


def test_round_up_and_nearest_are_distinguished():
    assert classify_behaviour(obs([(30.2, 31.0), (90.5, 91.0)])) == "round up"
    assert classify_behaviour(obs([(30.2, 30.0), (90.6, 91.0)])) == "round to nearest"


def test_quantum_reported_is_the_coarsest_consistent_one():
    # Whole seconds are divisible by every finer candidate too. Reporting 0.001 here would
    # claim the actuator is finer than the evidence supports.
    assert infer_quantum(obs([(10.0, 10.0), (20.0, 20.0)])) == 1.0


def test_half_second_receiver_is_not_mistaken_for_a_whole_second_one():
    assert infer_quantum(obs([(10.5, 10.5), (20.0, 20.0), (30.5, 30.5)])) == 0.5


def test_empty_observations_is_an_error_not_a_silent_pass():
    with pytest.raises(ValueError):
        infer_quantum([])
