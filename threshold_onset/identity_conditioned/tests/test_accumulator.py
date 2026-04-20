"""Tests for identity-conditioned accumulator."""

from __future__ import annotations

from threshold_onset.identity_conditioned import IdentityConditionedAccumulator


def test_record_and_distribution() -> None:
    acc = IdentityConditionedAccumulator()
    acc.record("a", "x", "ok", weight=2)
    acc.record("a", "x", "fail")
    assert acc.count("a", "x", "ok") == 2
    assert acc.total_for_pair("a", "x") == 3
    assert acc.outcome_distribution("a", "x") == {"fail": 1, "ok": 2}


def test_json_round_trip() -> None:
    acc = IdentityConditionedAccumulator()
    acc.record("p1", "stmt", "heard")
    acc.record("p2", "stmt", "ignored")
    blob = acc.to_jsonable()
    acc2 = IdentityConditionedAccumulator.from_jsonable(blob)
    assert acc2.count("p1", "stmt", "heard") == 1
    assert acc2.count("p2", "stmt", "ignored") == 1
