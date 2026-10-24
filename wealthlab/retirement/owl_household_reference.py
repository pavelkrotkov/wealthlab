"""Compare an independent solved retirement policy with the actual household ledger.

OWL chooses its own max-bequest policy. Native replay uses those gross IRA
orders, not an independently optimized policy. With zero returns and matching
spending, cumulative tax differences should explain marked-wealth differences.
That residual is an accounting diagnostic, not proof that tax forecasts agree.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.household.projection import project
from wealthlab.retirement.owl_household_compile import compile_case
from wealthlab.retirement.owl_household_solver import solve


def run(case):
    reference = solve(case)
    scenario = compile_case(case, reference)
    months = project(scenario)
    rows = compare(reference, months)
    return dict(
        case=case.model_dump(mode="json"),
        reference=reference,
        scenario=scenario.model_dump(mode="json"),
        rows=rows,
        household_months=months,
        max_absolute_wealth_residual=max(abs(r["wealth_tax_residual"]) for r in rows),
        funding_failure=any(r["funding_failure"] for r in months),
        unfilled_ira_requests=sum(r["ira_unfilled_requests"] for r in months),
        scope=SCOPE,
    )


def compare(reference, months):
    rows, cumulative = [], Decimal(0)
    for n, year in enumerate(reference["years"]):
        actual = [r for r in months if int(r["date"][:4]) == year]
        closing = actual[-1]
        tax = closing["annual_tax"]
        source_tax = amount(reference["federal_tax"][n]) + amount(reference["state_tax"][n])
        cumulative += tax["total_liability"] - source_tax
        wealth = sum(amount(b[n + 1]) for b in reference["balances"][0])
        row = dict(
            year=year,
            reference_federal_tax=amount(reference["federal_tax"][n]),
            native_federal_tax=tax["federal"]["income_tax"],
            native_nj_tax=tax["new_jersey"]["income_tax"],
            reference_agi=amount(reference["agi"][n]),
            native_agi=tax["federal"]["agi"],
            reference_total_deduction=amount(reference["deduction"][n]),
            native_standard_deduction=tax["federal"]["standard_deduction"],
            native_senior_deduction=tax["federal"]["senior_deduction"],
            reference_marked_wealth=wealth,
            native_marked_wealth=closing["net_wealth"],
            cumulative_tax_difference=cumulative,
            wealth_tax_residual=money(closing["net_wealth"] - wealth + cumulative),
            reference_spending=amount(reference["spending"][n]),
            **spending(actual),
            funding_failure=any(r["funding_failure"] for r in actual),
            unfilled_ira_requests=sum(r["ira_unfilled_requests"] for r in actual),
        )
        row.update(account_rows(reference, closing, n))
        rmd = closing["ira_annual_reconciliation"]["rmd"].values()
        row["native_rmd_shortfall"] = sum(r["shortfall"] for r in rmd)
        rows.append(row)
    return rows


def spending(actual):
    return dict(
        native_spending_paid=sum(r["essential"] for r in actual),
        native_spending_unfunded=sum(r["essential_unfunded"] for r in actual),
    )


def account_rows(reference, closing, n):
    result = {}
    for key, j in (("cash", 0), ("retirement", 1), ("roth", 2)):
        result[f"reference_{key}_balance"] = amount(reference["balances"][0][j][n + 1])
        result[f"native_{key}_balance"] = closing["account_balances"][key]
        if j:
            result[f"reference_{key}_withdrawal"] = amount(reference["withdrawals"][0][j][n])
    return result


def amount(value):
    return money(Decimal(str(value)))


SCOPE = (
    "One living single retiree, current-year January start, zero nominal returns/inflation, "
    "no SSA, employment, contributions, HSA, fees, Medicare or conversions. Traditional IRA "
    "has zero federal basis and explicitly full previously-taxed NJ principal; any Roth "
    "must meet this case's five-year history. Replay fixes OWL gross IRA withdrawals on "
    "January 1, spends monthly and settles native tax in December. OWL cash redeposits "
    "are internal transfers, never extra native income. Native federal taxes use each "
    "year's installed package law; OWL has its own forecasts, including its reported "
    "assumed OBBBA replacement year. Differences are reported, "
    "not eliminated. Marked wealth is not liquidation value. OWL's terminal estate proxy "
    "uses the supplied flat heirs tax and remains separate from native wealth; it can "
    "drive accelerated IRA withdrawal. This reference is not a household-optimal strategy."
)
