"""Public synthetic move cases retain independent federal and NJ income bases."""

from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.nj_residence import calculate
from wealthlab.tax.nj_residence_example import synthetic


def edited(change):
    data = synthetic().model_dump(mode="json")
    change(data["nj_residence"], data)
    return AnnualCase.model_validate(data)


def state(case):
    return calculate(
        case.nj_filing or case.filing,
        case.nj_income,
        case.nj_deductions,
        case.policy.year,
        case.nj_regime == "freeze_2025",
        profile=case.nj_residence,
    )


def results(case):
    return state(case)["residence_returns"]
