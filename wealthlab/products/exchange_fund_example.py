"""Original synthetic seven-year contract with no named sponsor or household facts."""

from datetime import date, timedelta

from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.tax.projection_example import template


def allocation(identity, when):
    return dict(id=identity, provenance="illustration", date=when, federal={}, new_jersey={})


def security(identity):
    return dict(
        id=identity,
        provenance="illustration",
        wash_group=identity,
        exposure_group=identity,
        kind="stock",
    )


def synthetic():
    data = household().model_dump(mode="json")
    data.update(name="Synthetic conditional exchange fund", end="2034-01-01", incomes=[])
    data["accounts"] = [
        dict(
            id="cash",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="cash",
            balance="30000",
            monthly_fee="0",
        ),
        dict(
            id="exchange",
            provenance="illustration",
            owner="person_a",
            currency="USD",
            wrapper="taxable",
            balance="100000",
            monthly_fee="0",
        ),
    ]
    data["expenses"][0]["monthly_amount"] = "300"
    scenario = Scenario.model_validate(data)
    plan = dict(
        account_id="exchange",
        nj_wash_treatment="no_wash_assumption",
        source_security=security("original"),
        source_lot=source_lot(),
        contribution_quantity="1000",
        accepted=True,
        opening_prices=dict(original="100", diversified_a="100", diversified_b="100"),
        federal_contribution="deferred",
        nj_contribution="deferred",
        federal_basket_distribution="deferred",
        nj_basket_distribution="deferred",
        liquid_after="2033-01-01",
        early_redemption="denied",
        annual_fee="0.0075",
        early_fee_fraction="0.02",
        basket=basket(),
        observations=observations(scenario),
        requests=[
            request("release", date(2033, 1, 31), "redeem"),
            request("exit", date(2033, 12, 31), "sell_liquid"),
        ],
        all_terms_tax_and_basis_assumptions_confirmed=True,
        other_tax_inputs_exclude_product_confirmed=True,
        no_external_substantially_identical_trades_confirmed=True,
    )
    data.update(exchange_fund_plan=plan, tax_plan=template(scenario).model_dump(mode="json"))
    return Scenario.model_validate(data)


def basket():
    return [
        dict(
            id=f"basket_{index}",
            provenance="illustration",
            security=security(identity),
            value_weight="0.5",
            federal_basis_weight="0.5",
            nj_basis_weight="0.5",
            federal_holding_start="2020-01-01",
        )
        for index, identity in enumerate(("diversified_a", "diversified_b"))
    ]


def observations(scenario):
    return [
        dict(
            id=f"mark_{i}",
            provenance="illustration",
            date=end - timedelta(days=1),
            prices=dict(original="100", diversified_a="100", diversified_b="100"),
            allocation=allocation(f"income_{i}", end - timedelta(days=1)),
        )
        for i, (_, end) in enumerate(months(scenario.start, scenario.end))
    ]


def request(identity, when, action):
    return dict(
        id=identity,
        provenance="illustration",
        date=when,
        action=action,
        early_tax=allocation(f"early_tax_{identity}", when),
    )


def source_lot():
    return dict(
        id="original_lot",
        provenance="illustration",
        account_id="exchange",
        security_id="original",
        acquired="2020-01-01",
        federal_holding_start="2020-01-01",
        liquid_after="2020-01-01",
        quantity="1000",
        federal_basis="20000",
        nj_basis="30000",
    )
