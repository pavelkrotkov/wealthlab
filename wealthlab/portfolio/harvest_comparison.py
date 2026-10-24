"""Compare shared scenario inputs while separating marked performance from tax liability."""

from decimal import Decimal


def compare(on, off):
    result = dict(holding=difference(on, off), harvesting_off=off)
    if "terminal_exit" in on:
        result["terminal_exit"] = difference(on["terminal_exit"], off["terminal_exit"])
    result["meaning"] = (
        "Same opening portfolio, dated inputs and fee schedule; actual harvesting commissions "
        "are charged only when traded. Tax differences are undiscounted annual liabilities, "
        "not cash payments. No reinvestment return on tax savings is assumed. "
        "Marked wealth adjusted by incremental liability is not household spendable wealth."
    )
    return result


def difference(on, off):
    annual = [
        dict(
            year=left["year"],
            tax_saving=right["with_lot_trades"]["total_liability"]
            - left["with_lot_trades"]["total_liability"],
        )
        for left, right in zip(
            on["annual_tax_comparison"], off["annual_tax_comparison"], strict=True
        )
    ]
    saving = sum((row["tax_saving"] for row in annual), Decimal(0)) if annual else None
    gross = on["gross_wealth"] - off["gross_wealth"]
    return dict(
        gross_wealth_on=on["gross_wealth"],
        gross_wealth_off=off["gross_wealth"],
        gross_wealth_difference=gross,
        annual_tax_savings=annual,
        total_tax_saving=saving,
        tax_adjusted_difference=None if saving is None else gross + saving,
        extra_cash_fees=on["fee_summary"]["cash_assessed"] - off["fee_summary"]["cash_assessed"],
        extra_transaction_costs=on["transaction_costs"] - off["transaction_costs"],
    )


def loss_summary(result):
    rows = [row for row in result["disposals"] if row["trade_id"] in result["harvest_sales"]]
    fields = (
        "federal_gross_gain",
        "federal_recognized_gain",
        "federal_wash_deferred",
        "federal_wash_permanent",
        "federal_pending_loss",
    )
    return {key: sum((row[key] for row in rows), Decimal(0)) for key in fields}
