"""Actual native shares/cash plus independent federal, PR and NJ gain bases."""

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan as lots
from wealthlab.tax.pr_execution_salary_example import monthly
from wealthlab.tax.pr_incentive_examples import legacy_dividends

SOURCE = (
    "Synthetic supplied source/basis/election/decree assumptions; no actual eligibility finding"
)


def synthetic_gain(treatment="incentive"):
    data = monthly().model_dump(mode="json")
    data["name"] = "Synthetic actual monthly wages and dated PR stock-gain execution"
    data["accounts"].append(
        dict(data["accounts"][0], id="brokerage", wrapper="taxable", balance="25000")
    )
    annual = data["tax_plan"]["cases"][0]
    gain = gain_row()
    annual["pr_federal"]["sources"].append(
        dict(
            id="stock_gain", owner_id="person_a", income=gain, classification_assumed_confirmed=True
        )
    )
    decree = legacy_dividends().decree.model_dump(mode="json")
    decree.update(annual_compliance_cost="250")
    annual["pr_federal"]["gain_profile"] = dict(
        treatment=treatment,
        local_us_credit_treatment="denied",
        decree=decree,
        gains=[
            dict(
                owner_id="person_a",
                source_id="stock_gain",
                sale_trade_id="stock_sale",
                facts=asset(),
            )
        ],
        compliance_expense_id="pr_compliance",
        other_preferential_entitlement="fails",
        source=SOURCE,
    )
    credit_profile(data, annual)
    data["expenses"] = [
        dict(
            id="pr_compliance",
            provenance="illustration",
            category="essential",
            start="2025-12-01",
            end="2026-01-01",
            monthly_amount="250",
            currency="USD",
            annual_growth=0,
        )
    ]
    data["lot_plan"] = stock_plan(Scenario.model_validate(data))
    return Scenario.model_validate(data)


def gain_row():
    return dict(
        received="2025-10-31",
        owner="primary",
        kind="long_term",
        federal_amount="10000",
        pr_amount="12000",
        federal_source="US",
        pr_source="US",
        evidence=SOURCE,
    )


def asset():
    return dict(
        income_index=0,
        acquired="2020-01-01",
        sale_proceeds="25000",
        federal_cost="15000",
        pr_cost="13000",
        federal_possession_start="2025-01-01",
        federal_move_fmv="20000",
        pr_move_fmv="20000",
        pr_resident_since="2025-01-01",
        ordinary_public_stock_classification="assumed",
        actively_traded_throughout="assumed",
        continuous_residence="assumed",
        us_non_bfr_in_prior_ten_years="yes",
        federal_fmv_election="assumed",
        evidence=SOURCE,
    )


def stock_plan(scenario):
    plan = lots(scenario)
    plan.update(funding_sources=[])
    for mark in plan["monthly_marks"]:
        mark["prices"] = dict(stock="100")
    plan["case"]["lots"] = [
        dict(
            id="opening_stock",
            provenance="illustration",
            account_id="brokerage",
            security_id="stock",
            acquired="2020-01-01",
            federal_holding_start="2020-01-01",
            liquid_after="2020-01-01",
            quantity="250",
            federal_basis="15000",
            nj_basis="16000",
        )
    ]
    plan["case"].update(
        closing_prices=dict(stock="100"),
        trades=[
            dict(
                id="stock_sale",
                provenance="illustration",
                date="2025-10-31",
                action="sell",
                account_id="brokerage",
                security_id="stock",
                quantity="250",
                price="100",
                commission="0",
                selection="specific",
                lot_ids=["opening_stock"],
            )
        ],
    )
    return plan


def credit_profile(data, annual):
    foreign = data["foreign_tax_plan"]
    profile = foreign["credit_profiles"][0]
    profile.update(annual=annual, eligibility="denied")
    profile["income"].append(
        dict(
            id="stock_gain",
            owner_id="person_a",
            country="US",
            kind="long_term",
            basket="passive",
            value=dict(
                date="2025-10-31",
                currency="USD",
                amount="10000",
                usd_per_unit="1",
                fx_source=SOURCE,
            ),
            source_classification=SOURCE,
        )
    )
