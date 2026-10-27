"""Admit only the documented ordinary-source form and effective-year profile.

Published2025 forms and an explicitly frozen policy share this limited
calculation. Preferential rates, losses, special deductions and AMT need
separate allocations. A blocked scope retains baseline tax and observed
foreign payments without publishing a favorable credit result.
"""

from wealthlab.tax.foreign_credit_classification import classification_reasons
from wealthlab.tax.foreign_credit_sources import SUPPORTED


def reasons(case, baseline):
    return policy_reasons(case) + income_reasons(case, baseline) + classification_reasons(case)


def policy_reasons(case):
    policy = case.annual.policy
    result = []
    if policy.year != 2025 and policy.mode != "freeze_2025":
        result.append(
            "This credit profile uses final2025 forms; later years need frozen2025 policy."
        )
    if case.eligibility == "unresolved" or not case.ordinary_source_and_tax_allocation_confirmed:
        result.append(
            "Confirm person eligibility and complete ordinary source/tax classifications."
        )
    if case.opening_carries and not case.carry_filing_unit_continuity_confirmed:
        result.append("Opening carry use needs confirmed person/filing-unit continuity.")
    return result


def income_reasons(case, baseline):
    fed, result = case.annual.federal_income, []
    if any(value for key, value in fed.model_dump().items() if key not in SUPPORTED):
        result.append(
            "Preferential/retirement/business/excluded-income/loss facts need another profile."
        )
    if baseline["federal"]["itemized_deduction"] or baseline["federal"]["senior_deduction"]:
        result.append("This allocation supports standard deduction without special adjustments.")
    if baseline["federal"]["amt"]:
        result.append("Computed AMT needs an independently supported AMT-credit allocation.")
    return result
