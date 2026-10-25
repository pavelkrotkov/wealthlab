"""Same requested HSA deposits, different actual payroll capacity under employer shocks."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.employer_example import synthetic as employer
from wealthlab.retirement.hsa_household_example import context
from wealthlab.retirement.hsa_household_template import template
from wealthlab.retirement.hsa_payroll_example import payroll


def synthetic(mode="deterministic", stress="early_crash"):
    household, market, binding = employer(mode, stress)
    data = household.model_dump(mode="json")
    data["name"] = "Synthetic HSA payroll funding and linked employment risk"
    data["accounts"].append(
        dict(
            id="cash_hsa",
            owner="person_a",
            wrapper="hsa",
            currency="USD",
            balance=2000,
            monthly_fee=0,
            provenance="illustration",
        )
    )
    plan = template(household)
    plan.update(
        years=[
            context(household, year) for year in range(household.start.year, household.end.year)
        ],
        conditional_nj_treatment_confirmed=True,
        cash_only_accounts_and_complete_context_confirmed=True,
        receipts_paid_before_projection_confirmed=True,
        employer_funding_excluded_from_other_nj_wages_confirmed=True,
        payroll=payroll(),
    )
    first = plan["payroll"]["orders"]
    first.extend(
        dict(o, id="next_" + o["id"], date=o["date"].replace("2026", "2027")) for o in list(first)
    )
    data["hsa_plan"] = plan
    return Scenario.model_validate(data), market, binding


def personal_policy(household):
    """Use the same requested schedule as ordinary personal cash deposits.

    No wages are required for an otherwise eligible personal HSA deposit.
    Actual funded contributions can therefore differ when work stops; this
    control deliberately displays that difference instead of claiming pure tax savings.
    """
    data = household.model_dump(mode="json")
    plan = data["hsa_plan"]
    if plan is None or plan["payroll"] is None:
        raise ValueError("A salary-reduction HSA plan is required for the personal control.")
    plan["contributions"] += [
        dict(**{k: v for k, v in order.items() if k != "owner"}, source="personal_cash")
        for order in plan["payroll"]["orders"]
    ]
    plan["payroll"] = None
    data["name"] += " — personal cash control"
    # Scenario names can already use the full input limit.
    data["name"] = data["name"][:120]
    return Scenario.model_validate(data)
