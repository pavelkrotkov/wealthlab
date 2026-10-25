"""Property liquidation actually funds previously unpaid costs before tax recognition."""

from decimal import Decimal as D

from drilling_cases import change, short

from wealthlab.products.drilling_compare import compare


def test_sale_proceeds_fund_idc_and_operating_creditors_with_ordinary_deductions():
    def edit(data):
        data["accounts"][0]["balance"] = "0"
        row = data["drilling_plan"]["observations"][0]
        row.update(capital_call="0", exit_gross_proceeds="120000")

    rows = compare(change(short(), edit))["rows"]["drilling"]
    row = rows[0]
    audit = row["drilling_audit"]["months"][0]
    assert audit["paid_costs"] == dict(
        operating_cost=D(0),
        manager_fee=D("10000"),
        liability_cost=D(0),
        idc_cost=D("70000"),
        tangible_cost=D("20000"),
        exit_cost=D(0),
    )
    assert (row["drilling_exit_cash"], row["drilling_creditor_payables"]) == (D("20000"), 0)
    # No contributed basis exists: funded IDC is independently basis limited to zero.
    assert row["annual_tax"]["federal"]["agi"] == D("20000")
