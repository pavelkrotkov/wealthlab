"""Acquisition and disposal exchange rates differ; ownership and exempt debt stay bounded."""

from decimal import Decimal

import pytest

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import amount, asset, synthetic
from wealthlab.tax.spain_inputs import SpainCase


def property_case():
    data = synthetic().model_dump(mode="json")
    home = asset("home", 1000000, False)
    home.update(
        kind="property", ownership_share=".5", treatment="principal_home", exemption_eur="300000"
    )
    data["assets"] = [home]
    data["debts"] = [
        dict(
            id="mortgage",
            owner_id="synthetic_person",
            ownership_share=".5",
            balance=amount(200000),
            deductible_eur="40000",
            related_asset_id="home",
            eligibility_source="Synthetic debt used to acquire the partially exempt home",
        )
    ]
    return data


def test_partial_home_exemption_and_related_mortgage_apply_to_the_owned_share():
    wealth = evaluate(SpainCase.model_validate(property_case()))["wealth"]["assessment"]
    assert wealth["gross_nonexempt"] == 200000
    assert wealth["deductible_debt"] == 40000
    assert wealth["net_base"] == 160000
    assert wealth["wealth_liability"] == 0


def test_financing_the_exempt_home_portion_does_not_create_an_extra_debt_deduction():
    data = property_case()
    data["debts"][0]["deductible_eur"] = "100000"
    with pytest.raises(ValueError, match="exempt asset portion"):
        SpainCase.model_validate(data)


def test_unlinked_debt_is_allocated_to_nonproductive_wealth_proportionately():
    data = synthetic().model_dump(mode="json")
    data["assets"] = [asset("productive", 1000, False), asset("other", 1000, True)]
    data["debts"] = [
        dict(
            id="general_debt",
            owner_id="synthetic_person",
            ownership_share="1",
            balance=amount(400),
            deductible_eur="400",
            related_asset_id=None,
            eligibility_source="Supplied qualifying personal debt",
        )
    ]
    wealth = evaluate(SpainCase.model_validate(data))["wealth"]["assessment"]
    assert wealth["net_base"] == Decimal(1600)
    assert wealth["nonproductive_net"] == Decimal(800)
