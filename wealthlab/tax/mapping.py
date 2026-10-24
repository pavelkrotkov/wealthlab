"""Explicit Tax-Calculator record mapping; capital character is never inferred from cash."""

from wealthlab.tax.facts import Deductions, FederalIncome
from wealthlab.tax.filing import Filing

INCOME_FIELDS = dict(
    wages_primary="e00200p",
    wages_spouse="e00200s",
    deferrals_primary="pencon_p",
    deferrals_spouse="pencon_s",
    interest="e00300",
    taxable_state_refund="e00700",
    tax_exempt_interest="e00400",
    dividends="e00600",
    qualified_dividends="e00650",
    ira_distributions="e01400",
    deductible_ira_contributions="e03150",
    retirement_additional_tax="e09900",
    taxable_pension="e01700",
    social_security="e02400",
    allowed_passive_income="e02000",
)
DEDUCTION_FIELDS = dict(
    medical="e17500",
    state_local_income_tax_paid="e18400",
    property_tax_paid="e18500",
    qualified_mortgage_interest="e19200",
    cash_charity="e19800",
    noncash_charity="e20100",
    eligible_care_expenses="e32800",
)


def record(filing: Filing, income: FederalIncome, deductions: Deductions, scale: float) -> dict:
    data = {
        target: float(getattr(income, source)) / scale for source, target in INCOME_FIELDS.items()
    }
    data.update(
        {
            target: float(getattr(deductions, source)) / scale
            for source, target in DEDUCTION_FIELDS.items()
        }
    )
    data.update(demographics(filing))
    data["e00200"] = data["e00200p"] + data["e00200s"]
    data["e01500"] = data["e01700"]
    short = income.short_term - income.short_carry
    long = income.long_term - income.long_carry
    data["p22250"], data["p23250"] = float(short) / scale, float(long) / scale
    # Schedule D 28% worksheet: LT carry and net ST loss reduce this component.
    special = max(0, income.collectibles_component - income.long_carry + min(0, short))
    data["e24518"] = float(special) / scale
    return data


def demographics(filing: Filing) -> dict:
    adult_count = 2 if filing.status == "joint" else 1
    return dict(
        RECID=1,
        MARS={"single": 1, "joint": 2, "separate": 3, "head": 4, "surviving": 5}[filing.status],
        age_head=filing.age_primary,
        age_spouse=filing.age_spouse,
        XTOT=adult_count + len(filing.dependents),
        n21=adult_count + sum(item.age >= 21 for item in filing.dependents),
        n24=sum(item.child_credit_eligible for item in filing.dependents),
        EIC=min(3, sum(item.earned_income_credit_eligible for item in filing.dependents)),
        f2441=sum(item.care_credit_eligible for item in filing.dependents),
        **dependent_ages(filing),
    )


def dependent_ages(filing: Filing) -> dict:
    bands = {"nu06": (0, 5), "nu13": (0, 12), "nu18": (0, 17), "n1820": (18, 20)}
    return {
        name: sum(low <= item.age <= high for item in filing.dependents)
        for name, (low, high) in bands.items()
    }
