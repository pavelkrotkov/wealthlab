"""Scale only new cash-only fixed-unit plans; actual native trades acquire every share.

The caller owns source-cash debit and account exclusivity and must reject an
existing household option plan. This helper cannot resize a live book or give
old lots a new basis. Absolute fees are supplied per unit, not inferred quotes.
"""

from wealthlab.portfolio.disposal import is_long
from wealthlab.products.option_household_inputs import OptionPlan
from wealthlab.products.option_household_scope import validate_tax
from wealthlab.products.option_household_validation import validate_confirmations
from wealthlab.products.option_opening import opening_state
from wealthlab.products.option_validation import validate


def scale_new_plan(unit_plan, count, *, per_unit_fees_confirmed):
    if type(count) is not int or not 1 <= count <= 100000:
        raise ValueError("Option allocation units must be positive bounded integers.")
    if per_unit_fees_confirmed is not True:
        raise ValueError(
            "Confirm every absolute stock/contract fee is supplied per allocation unit."
        )
    validate_profile(unit_plan)
    result = OptionPlan.model_validate(scaled_data(unit_plan, count))
    validate(result.case)
    validate_capacity(result.case)
    return result


def scaled_data(unit_plan, count):
    data = unit_plan.model_dump()
    case = data["case"]
    case["holdings"]["accounts"][0]["cash"] *= count
    case["stock_sale_fee"] *= count
    order = case["opening_stock_purchase"]
    if order is not None:
        order["shares"] *= count
        order["fee"] *= count
    for leg in case["legs"]:
        leg["contracts"] *= count
        leg["federal_character"] = new_character(case, leg)
        for field in ("opening_fee", "closing_fee", "expiry_fee"):
            leg[field] *= count
    return data


def validate_capacity(case):
    state, row = opening_state(case)
    if any((state.failures, row["collateral_shortfall"], row["cash"] < 0, state.loan)):
        raise ValueError(
            "Supplied option unit capital does not fund native opening trades/collateral."
        )


def required_capital(plan):
    """Opening native account cash, before actual purchases; no separate outside reserve."""
    validate(plan.case)
    validate_new_cash(plan.case)
    return plan.case.holdings.accounts[0].cash


def validate_profile(plan):
    validate(plan.case)
    validate_new_cash(plan.case)
    validate_tax(plan.case)
    validate_confirmations(plan)
    case = plan.case
    if any(leg.rolls_to or leg.opened != case.holdings.as_of for leg in case.legs):
        raise ValueError(
            "A fixed option allocation unit must open every supplied contract at start."
        )
    if any([*case.tax.federal_deferrals.values(), *case.tax.nj_deferrals.values()]):
        raise ValueError(
            "Position-specific deferred losses cannot be scaled into new option units."
        )
    if case.dividends and not plan.ordinary_dividend_tax_on_cash_receipt_confirmed:
        raise ValueError("Confirm the supported ordinary dividend cash-receipt tax assumption.")


def validate_new_cash(case):
    if case.holdings.lots or case.outside_cash or case.allow_settlement_loan:
        raise ValueError(
            "New option units require cash-only capital, no old lots or settlement loan."
        )
    if not case.unwind or case.holdings.accounts[0].cash <= 0:
        raise ValueError(
            "New option units require positive opening cash and actual complete unwind."
        )


def new_character(case, leg):
    # The declared legal class and unaffected-holding-period assumption stay
    # supplied; a fresh long capital contract still needs its actual calendar.
    if leg["side"] != "long" or leg["federal_class"] != "capital":
        return leg["federal_character"]
    realized = next(
        (event["date"] for event in case["events"] if event["leg_id"] == leg["id"]),
        min(leg["expiry"], case["holdings"]["end"]),
    )
    return "long_term" if is_long(leg["opened"], realized) else "short_term"
