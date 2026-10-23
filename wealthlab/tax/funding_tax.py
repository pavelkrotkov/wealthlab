"""Evaluate a proposed account sale without mutating cash, basis or recognized income."""

from decimal import Decimal

from wealthlab.tax import payments, state_deduction
from wealthlab.tax.annual import evaluate
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


def due(case, ledger, amounts, start, end) -> Decimal:
    case = state_deduction.add(
        case, ledger.outstanding["new_jersey"], ledger.plan.state_deduction_mode
    )
    result = evaluate(case)
    withholding = payments.withholding_request(amounts, ledger.plan, result, start, end)
    federal_cash = withholding["employee_payroll_withheld"] + withholding["federal_income_withheld"]
    federal_cash += withholding["federal_estimates"]
    nj_cash = withholding["nj_withheld"] + withholding["nj_estimates"]
    if payments.settlement_due(ledger.plan, start, end):
        nj_cash = max(nj_cash, result["nj_balance"])
    case = state_deduction.add(case, nj_cash, ledger.plan.state_deduction_mode)
    result = evaluate(case)
    if payments.settlement_due(ledger.plan, start, end):
        balances = payments.balances(result)
        # Scheduled withholding can exceed accrued liability; that overpayment is
        # still cash unavailable until the refund date, not spendable today.
        federal_cash = max(federal_cash, balances["federal"])
        nj_cash = max(nj_cash, balances["new_jersey"])
    return federal_cash + nj_cash + ledger.owed
