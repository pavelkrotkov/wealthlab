"""A later payment cannot retroactively fund an earlier country's paid-tax credit.

The native ledger legitimately pays US2025 arrears using an actual2026 wage
receipt. The PR2025 closing assessment cannot import that later cash without
its own dated reassessment; a favorable backdated result must be withheld.
"""

import pytest
from pr_execution_late_payment_case import late_payment

from wealthlab.household.projection import project
from wealthlab.tax.jurisdiction_execution import evaluate


def test_observer_retains_actual_december_payment_before_later_us_arrears_are_paid():
    observations = []
    project(late_payment(), tax_observer=observations.append)
    december = next(r for r in observations if r["date"] == "2025-12-31")
    assert december["closed_returns"][2025].net_paid["federal"] == 7650
    assert observations[-1]["closed_returns"][2025].net_paid["federal"] == 21099
    assert december["phase"] == "monthly"


def test_country_candidate_rejects_later_payment_instead_of_backdating_us_paid_tax():
    with pytest.raises(ValueError, match="Later US payment/return changes"):
        evaluate(late_payment())
