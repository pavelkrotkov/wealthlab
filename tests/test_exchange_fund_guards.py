"""Unknown legal facts and overlapping capital never silently choose favorable treatment."""

import pytest
from exchange_fund_cases import change, flat

from wealthlab.products.exchange_fund_household import Ledger


@pytest.mark.parametrize(
    "field",
    [
        "federal_contribution",
        "nj_contribution",
        "federal_basket_distribution",
        "nj_basket_distribution",
    ],
)
def test_unconfirmed_tax_treatment_blocks(field):
    with pytest.raises(ValueError, match="Unconfirmed"):
        Ledger(change(flat(), lambda d: d["exchange_fund_plan"].update({field: "unconfirmed"})))


@pytest.mark.parametrize(
    "field",
    [
        "all_terms_tax_and_basis_assumptions_confirmed",
        "other_tax_inputs_exclude_product_confirmed",
        "no_external_substantially_identical_trades_confirmed",
    ],
)
def test_missing_contract_or_tax_confirmation_blocks(field):
    with pytest.raises(ValueError, match="Confirm"):
        Ledger(change(flat(), lambda d: d["exchange_fund_plan"].update({field: False})))


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("quantity", "1001", "reconcile"),
        ("account_id", "cash", "belong"),
        ("security_id", "other", "belong"),
        ("acquired", "2026-01-02", "available"),
        ("liquid_after", "2026-01-02", "available"),
        ("id", "exchange_basket_0", "collides"),
    ],
)
def test_source_shares_must_be_actual_available_and_reconciled(field, value, message):
    def configure(data):
        data["exchange_fund_plan"]["source_lot"][field] = value

    with pytest.raises(ValueError, match=message):
        Ledger(change(flat(), configure))


def test_excess_contribution_and_other_transfer_destination_are_rejected():
    with pytest.raises(ValueError, match="exceeds"):
        Ledger(
            change(flat(), lambda d: d["exchange_fund_plan"].update(contribution_quantity="1001"))
        )

    def configure(data):
        data["contributions"] = [
            dict(
                id="transfer",
                provenance="assumption",
                start="2026-01-01",
                end="2027-01-01",
                monthly_amount="1",
                currency="USD",
                annual_growth=0,
                destination="exchange",
            )
        ]

    with pytest.raises(ValueError, match="share another"):
        Ledger(change(flat(), configure))
