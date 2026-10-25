"""Supported-profile boundaries prevent a successful baseline becoming a benefit claim."""


def guards(case):
    # A published-year label cannot silently carry into another comparison year.
    # Source classification and claim qualification are checked separately below.
    filing = case.baseline.filing
    reasons = []
    if filing.status not in {"single", "joint"}:
        reasons.append("PR profile supports single/joint adults without dependents.")
    if case.pr_regime == "published_2025" and case.baseline.policy.year != 2025:
        reasons.append("Choose explicit frozen 2025 PR law for a different comparison year.")
    return reasons + federal_guards(case) + source_guards(case) + claim_guards(case)


def source_guards(case):
    reasons = []
    if any(row.kind == "long_term" for row in case.income):
        reasons.append("Capital gains require the dated gain/preferential-tax profile.")
    if any("unset" in {row.federal_source, row.pr_source} for row in case.income):
        reasons.append("Each bucket needs independent federal and PR source classifications.")
    if case.baseline.filing.dependents:
        reasons.append("Dependent exemptions and credits require a separate supported profile.")
    return reasons


def federal_guards(case):
    filing = case.baseline.filing
    reasons = []
    if max(filing.age_primary, filing.age_spouse) >= 65:
        reasons.append("Senior deduction/exemption allocation needs a separate supported profile.")
    if any(case.baseline.federal_deductions.model_dump().values()):
        reasons.append("Federal adapter supports the allocated standard deduction only.")
    if case.pr_income_tax_paid_for_us_credit and not case.credit_evidence.strip():
        reasons.append("A positive US credit needs paid/accrued-tax allocation evidence.")
    return reasons


def claim_guards(case):
    from wealthlab.tax.pr_residence import MET

    reasons = []
    owners = {row.owner for row in case.income}
    if any(getattr(case, owner).us_citizen not in MET for owner in owners):
        reasons.append("This profile requires an explicit US-citizenship claim for every owner.")
    has_wages = any(row.kind == "wages" for row in case.income)
    if has_wages and case.pr_wages_reported_on_form_499r2 == "unset":
        reasons.append("Confirm or deny the PR wage-informative reporting assumption.")
    return reasons
