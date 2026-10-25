"""Supplied path values are separate from closed-contract cash and unknown taxes."""

from decimal import Decimal

from wealthlab.products.life_illustration import loan_review, net_value, shortfall

ZERO = Decimal(0)


def values(case, rows):
    contract = case.contract
    results = []
    for value in contract.values:
        previous = [r for r in rows if r["date"] <= value.date.isoformat()]
        loan = previous[-1]["loan_after"] if previous else contract.opening_loan
        review = loan_review(value.gross_cash_value, loan)
        confirmed = contract.values_match_executed_events_confirmed and not review
        net = {
            name: net_value(getattr(value, name), loan) if confirmed else None
            for name in ("gross_cash_value", "gross_surrender_value", "gross_death_benefit")
        }
        results.append(
            dict(
                **value.model_dump(mode="json"),
                loan_balance=loan,
                net_cash_value=net["gross_cash_value"],
                net_surrender_value=net["gross_surrender_value"],
                net_death_benefit=net["gross_death_benefit"],
                protection_shortfall=shortfall(case.insurance_need, net["gross_death_benefit"]),
                loan_contract_review_required=review,
                values_confirmed=confirmed,
            )
        )
    return results
