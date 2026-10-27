"""A failed full-exit request can later settle once actual capital pays creditors."""

from drilling_cases import change, short

from wealthlab.household.projection import project


def test_later_funded_full_sale_executes_once_then_retains_no_property_or_creditors():
    def edit(data):
        plan = data["drilling_plan"]
        plan["household_recourse_for_modeled_creditors"] = False
        first, second, last = plan["observations"]
        first.update(exit_requested=True, exit_gross_proceeds="40000", liability_cost="100000")
        second.update(
            capital_call="100000",
            exit_requested=True,
            exit_gross_proceeds="40000",
            distribution_request="0",
        )
        for field in (
            "production_units",
            "operating_cost",
            "residual_property_value",
            "distribution_request",
            "exit_gross_proceeds",
        ):
            last[field] = "0"
        last.update(exit_requested=False, deductions=[])

    rows = project(change(short(3), edit))
    first, second, last = rows
    assert (
        first["drilling_property_value"],
        first["drilling_creditor_payables"],
        first["drilling_exit_cash"],
    ) == (20000, 100000, 0)
    assert (
        second["drilling_production_receipts"],
        second["drilling_exit_cash"],
        second["drilling_creditor_payables"],
    ) == (1000, 40800, 0)
    assert (last["closing_cash"], last["drilling_property_value"], last["drilling_exit_cash"]) == (
        40800,
        0,
        0,
    )
    assert sum(r["drilling_call_funded"] for r in rows) == 200000
