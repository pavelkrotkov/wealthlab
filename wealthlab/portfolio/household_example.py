"""Synthetic dated retirement spending uses HIFO shares and actual separate bases."""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_deposit_household_example import synthetic as working


def synthetic():
    data = working().model_dump(mode="json")
    data.update(name="Synthetic actual-lot household funding", ira_plan=None)
    data["members"][0]["retirement_date"] = "2027-01-01"
    data["accounts"] = [data["accounts"][0]]
    data["accounts"][0]["balance"] = "1000"
    data["accounts"].append(
        dict(
            id="brokerage",
            provenance="illustration",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            balance="100000",
            monthly_fee="0",
        )
    )
    data["expenses"][0]["monthly_amount"] = "5000"
    case = Scenario.model_validate(data)
    data["lot_plan"] = plan(case)
    return Scenario.model_validate(data)


def plan(scenario):
    return dict(
        case=dict(
            as_of=scenario.start,
            end=scenario.end - timedelta(days=1),
            accounts=[
                dict(
                    id="brokerage",
                    provenance="illustration",
                    owner="primary",
                    wrapper="taxable",
                    cash="0",
                )
            ],
            securities=[
                dict(
                    id="stock",
                    provenance="illustration",
                    wash_group="stock",
                    kind="stock",
                    exposure_group="equity",
                )
            ],
            lots=[
                lot("low_basis", "400", "4000", "6000"),
                lot("high_basis", "600", "54000", "48000"),
            ],
            trades=[],
            closing_prices=dict(stock="130"),
            federal_wash_tracking=True,
            opening_wash_context_complete=True,
            nj_wash_treatment="no_wash_assumption",
        ),
        opening_prices=dict(stock="100"),
        monthly_marks=[
            dict(
                date=end - timedelta(days=1),
                prices=dict(stock="100" if start.year == 2026 else "130"),
            )
            for start, end in months(scenario.start, scenario.end)
        ],
        funding_sources=[
            dict(account_id="brokerage", security_id="stock", selection="hifo", commission="1")
        ],
        complete_ownership_and_outside_purchases_confirmed=True,
        monthly_settlement_and_cash_sweep_confirmed=True,
        funding_priority="linked_lots_before_other_permitted_accounts",
    )


def lot(identity, quantity, federal, nj):
    return dict(
        id=identity,
        provenance="illustration",
        account_id="brokerage",
        security_id="stock",
        acquired="2020-01-01",
        federal_holding_start="2020-01-01",
        liquid_after="2020-01-01",
        quantity=quantity,
        federal_basis=federal,
        nj_basis=nj,
        economic_basis=None,
    )
