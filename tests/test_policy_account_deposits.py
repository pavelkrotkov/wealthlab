"""Only executed deposits change assets; fixed employer benefits never become decisions."""

from optimization_account_cases import case

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


def funded_case():
    data = case().model_dump(mode="json")
    employer = dict(
        id="benefit",
        provenance="illustration",
        date="2026-01-01",
        destination="cash_hsa",
        source="direct_employer",
        amount="1000",
    )
    data["household"]["hsa_plan"]["contributions"] = [employer]
    personal = dict(employer, id="personal", source="personal_cash", amount="500")
    for choice in data["dimensions"][-1]["choices"]:
        choice["hsa_personal_contributions"] = [personal]
        choice["hsa_withdrawals"][0].update(amount="11500", date="2026-02-01")
    return PolicySearch.model_validate(data)


def test_personal_deposit_moves_actual_cash_but_only_fixed_employer_cash_adds_wealth():
    result = search(funded_case())
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        271999,
        271999,
    ]
    audit = result["selected_training"]["details"][0]["rows"][-1]["hsa_audit"]
    assert audit["receipt_remaining"]["past_medical"] == 500
    deposits = [r for r in audit["orders"] if r["kind"] in {"personal_cash", "direct_employer"}]
    assert [(r["kind"], r["funded"]) for r in deposits] == [
        ("direct_employer", 1000),
        ("personal_cash", 500),
    ]


def test_saving_after_final_tuition_cannot_make_residual_529_wealth_after_tax_cash():
    data = case().model_dump(mode="json")
    for choice in data["dimensions"][-1]["choices"]:
        choice["education_contributions"] = [
            dict(
                id="late_saving",
                provenance="illustration",
                date="2027-12-01",
                destination="college",
                amount="1000",
            )
        ]
    result = search(PolicySearch.model_validate(data))
    assert result["selection"] is None
    assert all(not c["constraints"]["completed_after_tax_exit"] for c in result["candidates"])
