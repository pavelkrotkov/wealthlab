"""Audit supplied policy cash flows without inventing a contract or household funding.

Living surrender and death are alternative terminal events. Full cash value and
full death benefit are never added together. All returns here are before tax;
actual household tax/loan/lapse funding belongs to the subsequent contract adapter.
"""

from wealthlab.products.dated_irr import calculate as irr
from wealthlab.products.life_illustration_flows import ZERO, cash, debt, totals


def run(study):
    return dict(
        synthetic=study.synthetic,
        inputs=study.model_dump(mode="json"),
        illustrations=[project(case, study) for case in study.illustrations],
    )


def project(case, study):
    rows = [point(case, row, study.insurance_need) for row in case.values]
    future = [
        f
        for f in case.flows
        if study.retirement_date is not None and f.date >= study.retirement_date
    ]
    return dict(
        id=case.id,
        name=case.name,
        scale=case.scale,
        source=case.source,
        funding_path=case.funding_path,
        rows=rows,
        totals=totals(case.flows),
        premiums_from_retirement=totals(future)["premium"]
        if study.retirement_date is not None
        else None,
        dated_cash=[
            dict(date=f.date.isoformat(), kind=f.kind, amount=f.amount, cash=cash(f))
            for f in case.flows
        ],
    )


def point(case, value, need):
    flows = [f for f in case.flows if f.date <= value.date]
    confirmed = (
        case.complete_history_from_issue_confirmed
        and case.values_match_cashflows_and_funding_path_confirmed
    )
    loan = debt(flows) if case.complete_history_from_issue_confirmed else None
    collateral_review = loan_review(value.gross_cash_value, loan)
    confirmed = confirmed and not collateral_review
    net = {
        key: net_value(getattr(value, key), loan) if confirmed else None
        for key in ("gross_cash_value", "gross_surrender_value", "gross_death_benefit")
    }
    surrender = net["gross_surrender_value"]
    death = net["gross_death_benefit"]
    return dict(
        date=value.date.isoformat(),
        **value.model_dump(exclude={"date"}),
        premium_paid=totals(flows)["premium"],
        loan_balance=loan,
        net_cash_value=net["gross_cash_value"],
        net_surrender_value=surrender,
        net_death_benefit=death,
        protection_shortfall=shortfall(need, death),
        cash_value_irr=terminal_irr(flows, value.date, net["gross_cash_value"]),
        surrender_irr=terminal_irr(flows, value.date, surrender),
        death_irr=terminal_irr(flows, value.date, death),
        values_confirmed=confirmed,
        loan_contract_review_required=collateral_review,
    )


def net_value(value, loan):
    return max(ZERO, value - loan) if value is not None and loan is not None else None


def terminal_irr(flows, when, terminal):
    if terminal is None:
        return dict(rate=None, status="missing value or unconfirmed cash-flow/funding history")
    return irr([*((f.date, cash(f)) for f in flows), (when, terminal)])


def loan_review(cash_value, loan):
    """The illustration alone cannot establish in-force status near loan exhaustion."""
    return loan is not None and loan > 0 and (cash_value is None or loan >= cash_value)


def shortfall(need, death):
    return max(ZERO, need - death) if need is not None and death is not None else None
