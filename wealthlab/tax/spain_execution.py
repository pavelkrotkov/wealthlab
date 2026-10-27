"""Pure Spain assessments consume real observed payments from the shared foreign book.

The three native taxes retain separate assessment identities. A scheduled IP
payment never becomes an SGF credit; only actual recognized payment records
feed the native country engine. Bilateral treaty credit allocation remains
explicitly denied/unresolved until a supported paid-US-tax bridge is supplied.
"""

from wealthlab.tax.spain_assessment_plan import assessment
from wealthlab.tax.spain_execution_payments import payments
from wealthlab.tax.spain_execution_validation import validate


def assessments(scenario, execution, observed=None):
    if execution is None:
        return {}, {}
    validate(scenario, execution)
    cash = payments(scenario, execution, observed)
    results, amounts = {}, {}
    for annual in execution.assessments.annuals:
        result = assessment_after_cash(annual, cash[annual.id])
        results[annual.id] = result
        for binding in execution.bindings:
            if binding.annual_id == annual.id:
                amounts[binding.foreign_assessment_id] = result["liabilities_eur"][binding.tax_type]
    return amounts, results


def assessment_after_cash(annual, cash):
    prior = {p.id: p for p in annual.case.payments}
    actual = {p.id: p for p in cash}
    if any(actual.get(identity) != value for identity, value in prior.items()):
        raise ValueError("Spain opening observations must match the actual single-book payments.")
    case = annual.case.model_copy(update=dict(payments=list(actual.values())))
    result = assessment(annual.model_copy(update=dict(case=case)))
    if any(value is None for value in result["liabilities_eur"].values()):
        raise ValueError("Unresolved Spain income/wealth classifications block country execution.")
    return result
