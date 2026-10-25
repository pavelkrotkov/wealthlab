"""Separate household audit output from numeric monthly funding columns."""


def completed(ledger):
    return ledger.summary if ledger else {}


def finish(ledger, rows):
    if ledger:
        rows[-1]["option_audit"] = ledger.log
        rows[-1]["option_mark_audit"] = ledger.state.rows
        rows[-1]["option_tax_audit"] = recognition_audit(ledger)
        rows[-1]["option_lots"] = [
            lot.model_dump(mode="json") for lot in ledger.state.book.lots.values()
        ]


def recognition_audit(ledger):
    from wealthlab.products.option_deferrals import validate as validate_deferrals
    from wealthlab.products.option_recognition import recognition
    from wealthlab.products.option_tax_rows import stock_recognition

    rows = recognition(ledger.state) + stock_recognition(ledger.state)
    validate_deferrals(ledger.plan.case.tax, rows)
    return rows
