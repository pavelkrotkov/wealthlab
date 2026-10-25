"""Public synthetic stock sale, dated capital calls and an illiquid QOF stock interest."""

from datetime import date, timedelta

from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan as lot_plan
from wealthlab.products.long_short_example import terms
from wealthlab.tax.projection_example import template


def synthetic(year=2027):
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic conditional QOZ household",
        start=f"{year}-01-01",
        end=f"{year + 12}-01-01",
        incomes=[],
        contributions=[],
        debts=[],
        expenses=[],
    )
    data["incomes"] = [
        dict(
            id="qoz_wages",
            provenance="illustration",
            owner="person_a",
            start=f"{year}-01-01",
            end=f"{year + 12}-01-01",
            monthly_amount="6000",
            currency="USD",
            annual_growth=0,
            stop_at_retirement=False,
        )
    ]
    data["accounts"] = [
        account("cash", "cash", "5000"),
        account("brokerage", "taxable", "100000"),
        account("qoz", "taxable", "0"),
    ]
    data["ytd"] = dict(gross_income="0", federal_tax_paid="0", state_tax_paid="0")
    scenario = Scenario.model_validate(data)
    linked = source_plan(scenario, year)
    case = economic_case()
    data.update(
        lot_plan=linked,
        tax_plan=template(scenario).model_dump(mode="json"),
        qoz_plan=contract(scenario, case, year),
    )
    return Scenario.model_validate(data)


def source_plan(scenario, year):
    linked = lot_plan(scenario)
    linked["case"]["lots"] = [
        dict(
            id="source_lot",
            provenance="illustration",
            account_id="brokerage",
            security_id="stock",
            acquired="2020-01-01",
            federal_holding_start="2020-01-01",
            liquid_after="2020-01-01",
            quantity="1000",
            federal_basis="20000",
            nj_basis="30000",
        )
    ]
    linked["case"]["trades"] = [
        dict(
            id="source_sale",
            provenance="illustration",
            date=f"{year}-01-15",
            account_id="brokerage",
            security_id="stock",
            action="sell",
            quantity="1000",
            price="100",
            commission="0",
            selection="specific",
            lot_ids=["source_lot"],
        )
    ]
    linked["funding_sources"] = []
    return linked


def economic_case():
    case = terms().model_dump(mode="json")
    case.update(
        opening_equity="1",
        outside_cash="0",
        long_multiple="1.3",
        short_multiple="0",
        annual_financing_rate=".04",
        annual_manager_fee=".01",
        turnover_cost="0",
        exit_cost="0",
        maintenance_fraction_of_gross=".20",
        rebalance="none",
        margin_policy="liquidate_on_breach",
        exit_at_horizon=False,
        redemptions=[],
    )
    return case


def account(identity, wrapper, balance):
    return dict(
        id=identity,
        provenance="illustration",
        owner="person_a",
        currency="USD",
        wrapper=wrapper,
        balance=balance,
        monthly_fee="0",
    )


def contract(scenario, economics, year):
    return dict(
        account_id="qoz",
        profile="direct_stock_gain_qof_c_corporation",
        federal="allowed",
        new_jersey="allowed",
        new_jersey_regime_and_basis_assumed_confirmed=True,
        unrelated_direct_gains_no_other_elections_assumed_confirmed=True,
        c_corporation_dividends_ep_no_extraordinary_distributions_assumed_confirmed=True,
        limited_liability_internal_debt_only_assumed_confirmed=True,
        calls_are_optional_partial_subscriptions_assumed_confirmed=True,
        entity_tax_already_in_returns_assumed_confirmed=True,
        source_and_product_tax_excluded_elsewhere_assumed_confirmed=True,
        terms_source_description="Invented QOF corporation terms, not a sponsor offer or forecast",
        economics=economics,
        preferred_hurdle=".06",
        carry_fraction=".20",
        calls=[
            dict(
                id="call_one",
                provenance="illustration",
                date=f"{year}-01-31",
                amount="80000",
                source_trade_id="source_sale",
                source_lot_id="source_lot",
            )
        ],
        observations=[
            dict(
                id=f"qoz_mark_{i}",
                provenance="illustration",
                date=end - timedelta(days=1),
                asset_return=".005",
            )
            for i, (_, end) in enumerate(months(scenario.start, scenario.end))
        ],
        sale_requested=date(year + 10, 1, 31),
        sale_not_before=date(year + 10, 7, 31),
        settlement_months=6,
    )
