"""Assessment, payment and unpaid liability have different cash and wealth effects."""

from decimal import Decimal

from tests.advisory_cases import plain, with_fee
from wealthlab.household.projection import project


def test_flat_thirty_day_fee_is_paid_once_without_product_basis_or_tax_deduction():
    case = with_fee(plain())
    before = case.model_dump_json()
    row = project(case)[0]
    assert row["advisory_fees_assessed"] == row["advisory_fees_paid"] == Decimal("83.33")
    assert row["advisory_fees_owed"] == row["fees_owed"] == 0
    assert row["closing_cash"] == Decimal("4916.67")
    assert row["net_wealth"] == Decimal("104916.67")
    assert case.model_dump_json() == before
    assert row["advisory_fee_audit"]["automatic_tax_deduction"] is False


def test_unfunded_bill_is_retained_once_as_liability_and_failure():
    row = project(with_fee(plain(cash="0")))[0]
    assert row["fees"] == row["closing_cash"] == 0
    assert row["advisory_fees_owed"] == row["fees_owed"] == Decimal("83.33")
    assert row["net_wealth"] == Decimal("99916.67")
    assert row["funding_failure"] is True


def test_partial_cash_and_existing_generic_fees_keep_separate_payment_attribution():
    case = plain(cash="100")
    cash = case.accounts[0].model_copy(update=dict(monthly_fee=Decimal(30)))
    case = case.model_copy(update=dict(accounts=[cash, *case.accounts[1:]]))
    row = project(with_fee(case))[0]
    # Native fixed $30 precedes this period's $83.33 outer charge: only $70 is paid.
    assert row["fees"] == 100
    assert row["advisory_fees_paid"] == 70
    assert row["fees_owed"] == row["advisory_fees_owed"] == Decimal("13.33")
    assert row["net_wealth"] == Decimal("99986.67")
