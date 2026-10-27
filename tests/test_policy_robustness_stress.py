"""Conditional stochastic stress and unsupported zero-price execution retain honest status."""

from optimization_cases import flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.robustness import check
from wealthlab.optimization.robustness_inputs import RobustnessCheck


def stress(shock, stochastic=False):
    case = flat()
    market = case.training.model_dump(mode="json")
    market.update(
        mode="stress",
        stress_base="monte_carlo" if stochastic else "deterministic",
        paths=2 if stochastic else 1,
        shocks=[dict(name="loss", month=0, mark_shocks=dict(equities=shock))],
    )
    item = RobustnessCheck.model_validate(dict(market=market))
    household = compile_candidate(case, [])
    return check(case, item, "frozen", household, household)


def test_named_stochastic_overlay_reports_conditional_sampling_only():
    result = stress(-0.4, stochastic=True)
    assert result["status"] == "passed"
    assert result["sampling_scope"] == "conditional_on_named_stress"
    assert result["selected"]["assessment"]["paths"] == 2
    assert result["selected"]["assessment"]["joint_success_95_wilson"] is not None


def test_unsupported_total_writeoff_keeps_error_instead_of_a_favorable_zero_tax_result():
    result = stress(-1)
    assert result["status"] == "unsupported"
    assert result["selected"]["results"] is None
    assert result["paired_changes"] is None
    assert "write-off adapter" in result["selected"]["unsupported_reason"]
