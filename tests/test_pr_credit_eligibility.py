"""A US NIIT credit classification is separate from the federal FTC tax base."""

from decimal import Decimal

import pytest

from wealthlab.tax.pr_candidate import conditional, paid_us_tax
from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_guards import guards
from wealthlab.tax.pr_inputs import income


def test_unresolved_niit_blocks_affected_pr_credit_instead_of_assuming_zero():
    row = synthetic().income[0].model_copy(update={"kind": "interest", "pr_source": "US"})
    us = {"income_tax": Decimal(20000), "niit": Decimal(3800)}
    with pytest.raises(ValueError, match="NIIT"):
        paid_us_tax(us, [row], [row])
    local_source = row.model_copy(update={"pr_source": "PR"})
    assert paid_us_tax(us, [local_source], [local_source]) == 16200


def test_unused_wage_reporting_claim_does_not_block_or_qualify_interest_only_case():
    case = synthetic()
    rows = [case.income[0].model_copy(update={"kind": "interest"})]
    baseline = case.baseline.model_copy(update={"federal_income": income(rows)})
    case = case.model_copy(
        update={"baseline": baseline, "income": rows, "pr_wages_reported_on_form_499r2": "unset"}
    )
    assert not guards(case)
    no_assumptions = {"primary": {"conditional": False}}
    assert not conditional(
        case.model_copy(update={"pr_wages_reported_on_form_499r2": "assumed"}), no_assumptions
    )
