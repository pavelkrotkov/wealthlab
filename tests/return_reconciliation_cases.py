"""A real high-income December return produces independently predictable revisions."""

from datetime import date

from tests.test_closed_return_positions import advance, empty_household
from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import evaluate
from wealthlab.tax.projection_ledger import TaxLedger


def close_december(cash, refund_month=4, overpaid=False, itemized=False, taxable_fraction=None):
    data = empty_household()
    data["start"] = "2026-12-01"
    data["accounts"][0]["balance"] = str(cash)
    data["tax_plan"]["refund_month"] = refund_month
    first = data["tax_plan"]["cases"][0]
    if itemized:
        first["federal_deductions"]["qualified_mortgage_interest"] = "50000"
    if taxable_fraction is not None:
        data["tax_plan"]["state_refund_taxable_fractions"] = {"2026": str(taxable_fraction)}
    first["federal_income"].update(wages_primary="200000", long_term="50000")
    first["nj_income"].update(wages="200000", dispositions="50000")
    if overpaid:
        base = Scenario.model_validate(data)
        assert base.tax_plan is not None
        result = evaluate(base.tax_plan.cases[0])
        first["payments"].update(
            federal_estimates=str(result["federal"]["income_tax"] + 1000),
            employee_payroll_withheld=str(result["federal"]["employee_payroll"]),
            nj_estimates=str(result["new_jersey"]["income_tax"] + 500),
        )
    case = Scenario.model_validate(data)
    taxes, wallet = TaxLedger(case.tax_plan, case), Wallet(case)
    advance(taxes, wallet, date(2026, 12, 1), date(2027, 1, 1))
    taxes.start_year(2027)
    return taxes, wallet


def allowed_loss(taxes):
    case = taxes.closed_returns[2026].case
    return case.model_copy(
        update=dict(
            federal_income=case.federal_income.model_copy(update=dict(long_term=40000)),
            nj_income=case.nj_income.model_copy(update=dict(dispositions=40000)),
        )
    )
