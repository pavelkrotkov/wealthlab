"""Evaluate a proposed account sale without mutating cash, basis or recognized income."""

from datetime import date
from decimal import Decimal

from wealthlab.tax import payments
from wealthlab.tax.liquidation import recognized


def proposal(case, source, bases, value, sold):
    federal_gain = recognized(value, bases[0], sold, source.loss_treatment)
    nj_gain = recognized(value, bases[1], sold, source.loss_treatment)
    federal = case.federal_income.model_copy(
        update={
            source.federal_character: getattr(case.federal_income, source.federal_character)
            + federal_gain
        }
    )
    nj = case.nj_income.model_copy(update={"dispositions": case.nj_income.dispositions + nj_gain})
    return case.model_copy(update={"federal_income": federal, "nj_income": nj})


def due(result: dict, ledger, amounts, start, end) -> Decimal:
    withholding = payments.withholding_request(amounts, ledger.plan, result, start, end)
    federal_cash = withholding["employee_payroll_withheld"] + withholding["federal_income_withheld"]
    federal_cash += withholding["federal_estimates"]
    nj_cash = withholding["nj_withheld"] + withholding["nj_estimates"]
    if end >= date(start.year + 1, 1, 1):
        balances = payments.balances(result)
        # December withholding can exceed final liability; that overpayment is
        # still cash unavailable until the refund date, not spendable today.
        federal_cash = max(federal_cash, balances["federal"])
        nj_cash = max(nj_cash, balances["new_jersey"])
    return federal_cash + nj_cash + ledger.owed
