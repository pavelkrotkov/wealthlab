"""NJ deductions use NJ gross income and explicit state eligibility, never federal AGI."""

from decimal import Decimal

from wealthlab.tax.filing import Filing
from wealthlab.tax.nj_facts import NJDeductions


def deductions(gross: Decimal, filing: Filing, inputs: NJDeductions) -> Decimal:
    medical = max(Decimal(0), inputs.medical - gross * Decimal(".02"))
    direct = inputs.qualified_msa + inputs.self_employed_health + inputs.alimony
    direct += (
        inputs.conservation + inputs.health_enterprise_zone + min(10000, inputs.organ_donation)
    )
    education = Decimal(0)
    if gross <= 200000:
        education = (
            min(10000, inputs.njbest) + min(2500, inputs.njclass) + min(10000, inputs.nj_tuition)
        )
    return medical + direct + education + exemptions(filing, inputs)


def exemptions(filing: Filing, inputs: NJDeductions) -> Decimal:
    adults = 2 if filing.status == "joint" else 1
    ages = [filing.age_primary] + ([filing.age_spouse] if adults == 2 else [])
    if max(inputs.blind_disabled_adults, inputs.veteran_adults) > adults:
        raise ValueError("NJ exemption counts exceed the adults on this return.")
    if inputs.qualifying_college_dependents > len(filing.dependents):
        raise ValueError("NJ college exemptions exceed listed dependents.")
    base = adults * 1000 + len(filing.dependents) * 1500
    base += (sum(age >= 65 for age in ages) + inputs.blind_disabled_adults) * 1000
    return Decimal(
        base + inputs.veteran_adults * 6000 + inputs.qualifying_college_dependents * 1000
    )
