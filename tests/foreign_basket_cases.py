"""Exact synthetic wage/interest allocations keep credit buckets separate from cash."""

from wealthlab.tax.foreign_credit_example import amount, synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def mixed_income():
    data = synthetic().model_dump(mode="json")
    data["annual"]["federal_income"].update(wages_primary="10000", interest="90000")
    data["annual"]["nj_income"].update(wages="10000", interest="90000")
    data["annual"]["payments"]["employee_payroll_withheld"] = "765"
    data["income"][0].update(country="ES", value=amount("2025-06-30", 10000))
    data["income"][1].update(kind="interest", basket="passive", value=amount("2025-06-30", 90000))
    data["tax_cash"][0].update(
        value=amount("2025-12-15", 5500), creditable_native="5500", income_ids=["work_us"]
    )
    data["passive_category_no_special_reclassification_confirmed"] = True
    return data


def split_payment():
    data = mixed_income()
    wage = data["tax_cash"][0]
    interest = dict(
        wage,
        id="interest_tax",
        basket="passive",
        income_ids=["work_es"],
        value=amount("2025-12-15", 3500),
        creditable_native="3500",
    )
    wage.update(value=amount("2025-12-15", 2000), creditable_native="2000")
    data["tax_cash"].append(interest)
    return ForeignCreditCase.model_validate(data)
