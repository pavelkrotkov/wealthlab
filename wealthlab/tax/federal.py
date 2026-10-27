"""Annual federal tax adapter, with income tax and employee payroll separated once."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.capital import next_carry
from wealthlab.tax.facts import Deductions, FederalIncome
from wealthlab.tax.federal_engine import values as engine_values
from wealthlab.tax.filing import Filing
from wealthlab.tax.mapping import record
from wealthlab.tax.policy import TaxPolicy

OUTPUTS = (
    "iitax",
    "c09200",
    "ptax_was",
    "ptax_amc",
    "niit",
    "c00100",
    "c02500",
    "c04800",
    "c01000",
    "c04470",
    "standard",
    "c04600",
    "qbided",
    "c09600",
    "refund",
    "senior_deduction",
    "taxbc",
    "c05800",
    "c07300",
)


def calculate(
    filing: Filing, income: FederalIncome, deductions: Deductions, policy: TaxPolicy, credits=None
) -> dict:
    year, scale, label = policy.valuation()
    validate_credit(credits, filing, income, deductions, policy)
    if filing.status != "joint" and (income.wages_spouse or income.deferrals_spouse):
        raise ValueError("Spouse wage inputs are supported only on joint returns.")
    raw = engine_values(
        record(filing, income, deductions, scale, credits),
        year,
        OUTPUTS,
        insurance_niit=float(income.insurance_ordinary_income) / scale,
    )
    values = {key: money(value * scale) for key, value in raw.items()}
    return breakdown(values, income, label)


def breakdown(values: dict, income: FederalIncome, label: str) -> dict:
    # Use the Form 1040 total, which is invariant to Tax-Calculator's soi_iitax
    # reporting switch. NIIT stays in income tax; additional Medicare is payroll.
    regular_payroll = values["ptax_was"] / 2
    income_tax = values["c09200"] - values["refund"] - values["ptax_amc"]
    taxable_unfloored = (
        values["c00100"]
        - values["c04470"]
        - values["standard"]
        - values["c04600"]
        - values["senior_deduction"]
    )
    carried = next_carry(
        income.short_term - income.short_carry,
        income.long_term - income.long_carry,
        taxable_unfloored,
        max(Decimal(0), -values["c01000"]),
    )
    return dict(
        income_tax=income_tax,
        tax_before_credits=values["c05800"],
        regular_tax_before_credits=values["taxbc"],
        foreign_tax_credit=values["c07300"],
        employee_payroll=regular_payroll + values["ptax_amc"],
        additional_medicare=values["ptax_amc"],
        niit=values["niit"],
        total=income_tax + regular_payroll + values["ptax_amc"],
        agi=values["c00100"],
        gross_social_security=income.social_security,
        taxable_social_security=values["c02500"],
        taxable_income=values["c04800"],
        standard_deduction=values["standard"],
        senior_deduction=values["senior_deduction"],
        itemized_deduction=values["c04470"],
        amt=values["c09600"],
        short_carry=carried["short_term"],
        long_carry=carried["long_term"],
        insurance_ordinary_income=income.insurance_ordinary_income,
        insurance_additional_tax=income.insurance_additional_tax,
        ordinary_noninvestment_income=income.ordinary_noninvestment_income,
        ordinary_noninvestment_adapter=(
            "Explicit e00800 numerical carrier with inclusion=1; no statutory alimony input"
            if income.ordinary_noninvestment_income
            else None
        ),
        policy=label,
    )


def validate_credit(credits, filing, income, deductions, policy):
    if credits is None or credits.eligibility != "allowed" or not credits.regular:
        return
    baseline = calculate(filing, income, deductions, policy)
    if credits.regular > baseline["regular_tax_before_credits"]:
        raise ValueError("Permitted regular foreign credit exceeds regular tax before credits.")
