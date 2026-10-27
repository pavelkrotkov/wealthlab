"""Cash exits do not waive independent contractual rights or tax recognition.

An unknown no-future-rights assertion retains the same $282,338 cash as the
complete case while preventing after-tax ranking. Declared later allocations
remain visible until recognized; out-of-horizon events require a longer
projection. Missing native audits must fail closed, including
when visible account balances have already fallen to zero. Deferred losses
remain unresolved economic tax attributes rather than a fabricated cash saving.
"""

from copy import deepcopy

import pytest
from optimization_cases import changed
from optimization_contract_cases import case

from wealthlab.markets.paths import generate
from wealthlab.optimization.contract_exits import employer_closed, options_closed
from wealthlab.optimization.search import evaluate, search


def execute(profile):
    return evaluate(profile, [profile.dimensions[0].choices[0]], 0, generate(profile.training))


def test_missing_termination_facts_preserve_cash_but_withhold_completed_exit_ranking():
    def edit(data):
        events = data["household"]["compensation_plan"]["events"]
        next(e for e in events if e["kind"] == "termination")["no_future_rights"] = None

    candidate, result = execute(changed(case(), edit))
    assert result["details"][0]["rows"][-1]["closing_cash"] == 282338
    assert not candidate["constraints"]["completed_after_tax_exit"]
    assert candidate["median_real_after_tax_exit_wealth"] is None


def test_later_tax_allocations_are_recognized_after_actual_contract_termination():
    def edit(data):
        events = data["household"]["compensation_plan"]["events"]
        original = next(e for e in events if e["kind"] == "allocation")
        events.append(dict(original, id="later_tax", date="2027-02-01"))

    profile = changed(case(), edit)
    _, result = execute(profile)
    rows = result["details"][0]["rows"]
    baseline = search(case())["selected_training"]["details"][0]["rows"]
    assert rows[11]["closing_cash"] == baseline[11]["closing_cash"]
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 24999
    final = rows[-1]["employer_tranches"][0]["exit_evidence"]
    assert final["future_supplied_tax_allocations_clear"] is True
    assert employer_closed(profile.household, rows[-1])


def test_out_of_horizon_tax_allocation_requires_extending_the_actual_projection():
    def edit(data):
        events = data["household"]["compensation_plan"]["events"]
        original = next(e for e in events if e["kind"] == "allocation")
        events.append(dict(original, id="later_tax", date="2028-02-01"))

    candidate, result = execute(changed(case(), edit))
    assert result is None and not candidate["eligible"]
    assert "inside the household projection" in candidate["unsupported_reason"]


@pytest.fixture(scope="module")
def actual():
    profile = case()
    return profile, search(profile)["selected_training"]["details"][0]["rows"][-1]


def test_deferred_or_unresolved_option_tax_never_becomes_zero_terminal_tax(actual):
    profile, original = actual
    row = deepcopy(original)
    row["option_tax_audit"][0]["deferred"] = 1
    assert not options_closed(profile.household, row)
    row["option_tax_audit"][0].update(deferred=0, recognized=None)
    assert not options_closed(profile.household, row)
