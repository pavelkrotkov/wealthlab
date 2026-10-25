"""Every supplied annual baseline remains visible, including years without policy events."""

from tests.life_contract_cases import case, event
from wealthlab.products.life_contract import run
from wealthlab.products.life_contract_inputs import LifeContractCase
from wealthlab.tax.annual import synthetic


def with_baselines(contract_case):
    data = contract_case.model_dump(mode="json")
    baseline = synthetic().model_dump(mode="json")
    following = synthetic().model_dump(mode="json")
    following["policy"].update(year=2026, mode="freeze_2025")
    following["nj_regime"] = "freeze_2025"
    data["annual_cases"] = {2025: baseline, 2026: following}
    return LifeContractCase.model_validate(data)


def test_eventless_baseline_year_is_compared_and_retained_in_output():
    result = run(with_baselines(case([event("surrender", 150)])))
    assert [r["year"] for r in result["annual"]] == [2025, 2026]
    after = result["annual"][1]
    assert after["tax_change"] == 0
    assert after["with_policy"] == after["baseline"]
    assert after["recognition"]["federal_ordinary_income"] == 0


def test_no_events_still_reports_each_supplied_baseline():
    result = run(with_baselines(case()))
    assert [r["year"] for r in result["annual"]] == [2025, 2026]
    assert [r["tax_change"] for r in result["annual"]] == [0, 0]


def test_unknown_contract_with_no_events_cannot_imply_a_zero_tax_conclusion():
    result = run(with_baselines(case(ordinary_personal_contract_confirmed=False)))
    assert len(result["annual"]) == 2
    assert all(r["tax_change"] is None for r in result["annual"])
    assert all("federal_ordinary_income" in r["unknown_fields"] for r in result["annual"])
