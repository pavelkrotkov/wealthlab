"""Original two-month household shows actual strike delivery funding ordinary spending."""

from datetime import date, timedelta

from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.products.option_example import synthetic as contracts
from wealthlab.products.option_household_inputs import OptionPlan
from wealthlab.tax.projection_example import template


def synthetic():
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic actual household option assignment",
        start="2026-01-01",
        end="2027-01-01",
        incomes=[],
        expenses=[],
        debts=[],
        contributions=[],
    )
    data["accounts"] = [
        dict(
            id="cash",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="cash",
            balance="1000",
            monthly_fee="0",
        ),
        dict(
            id="options",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="taxable",
            balance="10000",
            monthly_fee="0",
        ),
    ]
    data["expenses"] = [
        dict(
            id="living",
            provenance="illustration",
            start="2026-01-01",
            end="2027-01-01",
            monthly_amount="500",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    scenario = Scenario.model_validate(data)
    return scenario.model_copy(
        update=dict(
            tax_plan=template(scenario),
            option_plan=OptionPlan.model_validate(
                dict(
                    account_id="options",
                    case=option_case(),
                    actual_household_cash_confirmed=True,
                    tax_history_and_no_duplicate_income_confirmed=True,
                    priority="after_prior_tax_arrears_before_sleeves_and_wrapper_deposits",
                )
            ),
        )
    )


def option_case():
    data = contracts("Covered call").model_dump(mode="json")
    book = data["holdings"]
    book.update(as_of="2026-01-01", end="2026-12-31")
    book["accounts"][0].update(id="options", cash="0")
    book["lots"][0]["account_id"] = "options"
    data["legs"][0].update(
        opened="2026-01-01", expiry="2026-02-28", premium="5", opening_fee="0", closing_fee="0"
    )
    marks = [("2026-01-01", "100"), ("2026-01-31", "105")]
    marks += [
        (str(end - timedelta(days=1)), "120")
        for start, end in months(date(2026, 2, 1), date(2027, 1, 1))
    ]
    data["marks"] = [dict(data["marks"][0], date=day, stock=spot) for day, spot in marks]
    data.update(outside_cash="0", dividends=[], unwind=True, stock_sale_fee="0")
    data["tax"].update(
        federal_rules="conditional_capital",
        nj_rules="conditional_realized_capital",
        straddle="assume_not_applicable",
        covered_call="assume_qualified",
        constructive_sale="assume_not_applicable",
        holding_period="supplied_unaffected",
        nj_premium_basis="assume_same_mechanics",
    )
    return data
