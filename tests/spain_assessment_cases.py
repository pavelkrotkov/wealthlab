"""Original single-assessment plan for payment and schedule reconciliation checks."""

from wealthlab.tax.spain_assessment_example import synthetic_plan


def single():
    data = synthetic_plan().model_dump(mode="json")
    data["annuals"] = data["annuals"][:1]
    return data
