"""Observe dated NJ and prepared PR facts in the same live household tax month."""

from datetime import timedelta

from wealthlab.tax.nj_residence_household import observe as nj_observe


def observe(case, end):
    case = nj_observe(case, end)
    if case.pr_federal is not None:
        profile = case.pr_federal.model_copy(update=dict(as_of=end - timedelta(days=1)))
        case = case.model_copy(update=dict(pr_federal=profile))
    return case
