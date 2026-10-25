"""The trial taxable-sale funding quote includes the same NJ withholding as actual payroll."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from wealthlab.retirement.hsa_payroll_example import synthetic
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.funding_tax import due


def test_tax_funding_quote_restores_state_wages_without_restoring_federal_fica():
    scenario = synthetic()
    data = scenario.tax_plan.cases[0].model_dump(mode="json")
    data["federal_income"].update(wages_primary="7500", deferrals_primary="2000")
    data["nj_income"].update(wages="8500")
    case = AnnualCase.model_validate(data)
    ledger = SimpleNamespace(
        plan=scenario.tax_plan,
        owed=0,
        outstanding=dict(federal=Decimal(0), new_jersey=Decimal(0)),
        nj_wage_withholding_addition=Decimal(500),
    )
    amounts = {scenario.incomes[0].id: Decimal(7500)}
    assert due(case, ledger, amounts, date(2026, 1, 1), date(2026, 2, 1)) == Decimal("2626.75")
    ledger.nj_wage_withholding_addition = Decimal(0)
    assert due(case, ledger, amounts, date(2026, 1, 1), date(2026, 2, 1)) == Decimal("2601.75")
