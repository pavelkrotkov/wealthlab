"""Auditable annual mainland comparison; monthly relocation remains issue 17."""

from wealthlab.tax.annual import evaluate as mainland
from wealthlab.tax.pr_candidate import candidate
from wealthlab.tax.pr_guards import guards
from wealthlab.tax.pr_inputs import validate
from wealthlab.tax.pr_residence import federal_status

LIMITATION = (
    "Annual federal/PR comparison only. PR ordinary-rate election; no decree benefit inferred. "
    "NJ departure, monthly household cash and optimizer linkage remain cross-border issue 17. "
    "Baseline NJ stays an independent mainland input; state relocation savings are not asserted."
)


def evaluate(case):
    validate(case)
    baseline = mainland(case.baseline)
    reasons = guards(case)
    statuses = {
        owner: federal_status(getattr(case, owner), case.baseline.policy.year)
        for owner in {row.owner for row in case.income}
    }
    reasons += [reason for status in statuses.values() for reason in status["reasons"]]
    result = dict(
        baseline=baseline,
        residence=statuses,
        reasons=reasons,
        limitation=LIMITATION,
        configuration=case.model_dump(mode="json"),
    )
    if reasons:
        return dict(result, candidate=None)
    try:
        result["candidate"] = candidate(case, baseline, statuses)
    except ValueError as error:
        result.update(candidate=None, reasons=[str(error)])
    return result
