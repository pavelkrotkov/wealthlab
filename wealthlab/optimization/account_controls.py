"""Native account schedules reuse shared books and fixed eligibility/basis history.

Only personal HSA deposits are decisions; employer compensation stays fixed.
HSA withdrawal dates/amounts may change, but their source, receipts and tax
classification retain the baseline order identity and independently supplied
NJ treatment. Removing an order removes only its unused tax-map entry.
"""

from wealthlab.retirement.contribution_inputs import ContributionOrder
from wealthlab.retirement.education_inputs import EducationContribution
from wealthlab.retirement.hsa_inputs import HSAContribution, HSAWithdrawal
from wealthlab.retirement.workplace_inputs import WorkplaceOrder
from wealthlab.retirement.workplace_withdrawal_inputs import WorkplaceCashOrder
from wealthlab.tax.facts import TaxModel

PATHS = {
    "ira_contributions": ("ira_plan", "contributions", "orders"),
    "workplace_contributions": ("workplace_plan", "orders"),
    "workplace_cash_orders": ("workplace_plan", "cash_withdrawals", "orders"),
    "workplace_roth_orders": ("workplace_plan", "roth_cash_withdrawals", "orders"),
    "education_contributions": ("education_plan", "contributions"),
}


class AccountControls(TaxModel):
    ira_contributions: list[ContributionOrder] | None = None
    workplace_contributions: list[WorkplaceOrder] | None = None
    workplace_cash_orders: list[WorkplaceCashOrder] | None = None
    workplace_roth_orders: list[WorkplaceCashOrder] | None = None
    education_contributions: list[EducationContribution] | None = None
    hsa_personal_contributions: list[HSAContribution] | None = None
    hsa_withdrawals: list[HSAWithdrawal] | None = None


def apply(data, choice):
    for name, path in PATHS.items():
        orders = getattr(choice, name)
        if orders is not None:
            plan = configured(data, path[:-1])
            plan[path[-1]] = [o.model_dump(mode="json") for o in orders]
    if choice.hsa_personal_contributions is not None:
        personal_deposits(configured(data, ("hsa_plan",)), choice.hsa_personal_contributions)
    if choice.hsa_withdrawals is not None:
        withdrawals(configured(data, ("hsa_plan",)), choice.hsa_withdrawals)


def configured(data, path):
    for key in path:
        data = data[key]
        if data is None:
            raise ValueError(f"Account policy choices require an existing configured {key}.")
    return data


def personal_deposits(plan, orders):
    if any(o.source != "personal_cash" for o in orders):
        raise ValueError("HSA personal contribution choices cannot change employer funding.")
    employer = [o for o in plan["contributions"] if o["source"] == "direct_employer"]
    # Fixed employer funding has priority over chosen personal deposits on a tie.
    plan["contributions"] = [*employer, *(o.model_dump(mode="json") for o in orders)]


def withdrawals(plan, orders):
    originals = {o["id"]: o for o in plan["withdrawals"]}
    changed = [o.model_dump(mode="json") for o in orders]
    for order in changed:
        original = originals.get(order["id"])
        if original is None or fixed_terms(order) != fixed_terms(original):
            raise ValueError("HSA choices may change only existing withdrawal dates and amounts.")
    plan["withdrawals"] = changed
    retain_tax_entries(plan, changed)


def retain_tax_entries(plan, changed):
    retained = {o["id"] for o in changed} | {b["id"] for b in plan["medical_bills"]}
    plan["nj_withdrawal_taxable_fractions"] = {
        key: value
        for key, value in plan["nj_withdrawal_taxable_fractions"].items()
        if key in retained
    }


def fixed_terms(order):
    return {key: value for key, value in order.items() if key not in {"date", "amount"}}
