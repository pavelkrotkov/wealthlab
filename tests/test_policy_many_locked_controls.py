"""Many independent locked policies remain cheap under the unchanged actual work budget."""

from optimization_qoz_cases import case, changed

from wealthlab.optimization.search import search
from wealthlab.optimization.validation import validate


def test_nine_locked_controls_run_one_allowed_candidate_without_relaxing_work_limits():
    def edit(data):
        data["dimensions"][0]["locked_choice"] = "no_entry"
        controls = [
            dict(retirement_dates={"person_a": "2027-01-01"}),
            dict(retirement_dates={"person_b": "2027-01-01"}),
            dict(change_guardrail=True),
            dict(sale_policies=[]),
            dict(harvest_policies=[]),
            dict(rebalances=[]),
            dict(savings=[]),
            dict(lot_funding_order=[]),
        ]
        data["dimensions"] += [
            dict(id=f"locked_{i}", locked_choice="fixed", choices=[dict(id="fixed", **control)])
            for i, control in enumerate(controls)
        ]
        data.update(maximum_candidates=1, maximum_projection_months=24)

    profile = changed(case(), edit)
    assert validate(profile) == 1
    result = search(profile)
    assert result["evaluated_candidates"] == 1
    candidate = result["candidates"][0]
    assert "unsupported_reason" not in candidate
    assert candidate["median_marked_real_wealth"] == 105000
    assert candidate["constraints"]["completed_after_tax_exit"] is False
