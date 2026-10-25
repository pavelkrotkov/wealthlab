"""Fund cash/K-1 facts are not dividends or basis changes on directly owned shares.

A paired run must explicitly authorize that distinction when nonzero fund facts
are supplied. The direct leg then reports every exclusion; it cannot silently
convert partnership distributions into tax-free direct-ownership receipts.
"""

from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome


def fund_income(observation):
    allocation = observation.allocation
    return allocation.federal != FederalIncome() or allocation.new_jersey != NJIncome()


def has_fund_facts(observation):
    return any(
        (
            observation.distribution,
            observation.federal_basis_adjustment,
            observation.nj_basis_adjustment,
            fund_income(observation),
        )
    )


def validate(plan):
    if plan.mode != "direct_sale":
        return
    if any(has_fund_facts(o) for o in plan.observations) and not (
        plan.fund_specific_flows_excluded_from_direct_sale_confirmed
    ):
        raise ValueError(
            "Confirm fund-specific cash, basis and tax exclusions from direct ownership."
        )


def audit(plan, observation):
    direct = plan.mode == "direct_sale"
    return dict(
        excluded_fund_distribution=observation.distribution if direct else 0,
        excluded_fund_federal_basis_adjustment=observation.federal_basis_adjustment
        if direct
        else 0,
        excluded_fund_nj_basis_adjustment=observation.nj_basis_adjustment if direct else 0,
        excluded_fund_tax_allocation=int(direct and fund_income(observation)),
        direct_basket_already_owned_requests=0,
        inactive_fund_redemption_requests=0,
    )
