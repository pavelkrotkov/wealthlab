"""Monthly synthetic source rows expose production and claim stress without provider forecasts.

Zero fields are explicit original illustration inputs, rather than defaults
applied to an incomplete household or unknown sponsor contract.
"""

from decimal import Decimal

from wealthlab.products.drilling_example_terms import deduction


def observation(i, when, profile):
    data = base(i, when)
    if profile == "poor_production":
        data.update(
            production_units="0",
            residual_property_value="0",
            distribution_request="0",
            reference_cash_request="0",
            exit_gross_proceeds="0",
        )
    if profile == "liability_call" and i == 6:
        data["liability_cost"] = "150000"
    treatment = profile if profile in {"denied", "deferred"} else "allowed"
    cost = sum(Decimal(data[k]) for k in ("operating_cost", "manager_fee", "liability_cost"))
    data["deductions"] = [
        deduction(f"operating_{i}", "operating_loss", cost, treatment),
        deduction(f"idc_{i}", "idc", 70000, treatment),
    ]
    data["supplemental_federal"] = supplements(i, when.year, profile, treatment)
    return data


def base(i, when):
    zero = (
        "production_units",
        "capital_call",
        "operating_cost",
        "idc_cost",
        "tangible_cost",
        "manager_fee",
        "liability_cost",
        "distribution_request",
        "exit_gross_proceeds",
        "exit_fee",
        "reference_cash_request",
    )
    data: dict = dict.fromkeys(zero, "0")
    data.update(
        id=f"well_month_{i}",
        provenance="illustration",
        date=when,
        commodity_price="100",
        royalty_fraction="0",
        residual_property_value="20000",
        reference_price="100",
        reference_locked=False,
        exit_requested=False,
    )
    if i == 0:
        data.update(
            capital_call="100000", idc_cost="70000", tangible_cost="20000", manager_fee="10000"
        )
    else:
        data.update(
            production_units="10",
            operating_cost="200",
            distribution_request="600",
            reference_cash_request="600",
        )
    if i == 23:
        data.update(
            exit_requested=True,
            exit_gross_proceeds="40000",
            distribution_request="0",
            reference_cash_request="0",
        )
    return data


def supplements(i, year, profile, treatment):
    result = dict(partnership_se_earnings_primary="0")
    if year == 2027 and profile != "poor_production":
        result["partnership_se_earnings_primary"] = "800"
    if i == 0 and treatment == "allowed":
        result["additional_amt_income"] = "70000"
    return result
