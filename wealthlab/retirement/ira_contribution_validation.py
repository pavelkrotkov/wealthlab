"""A combined IRA cash book has one opening context and one set of dated deposits.

The existing contribution model owns eligibility and annual limits. Its cash
and account context must agree with the withdrawal model, rather than becoming
another source of money. Actual funded deposits determine basis additions.
"""


def validate(case):
    plan = case.contributions
    if plan is None:
        return
    if not case.contribution_context_confirmed:
        raise ValueError(
            "Confirm annual IRA contribution compensation, MAGI and complete elections."
        )
    if plan.year != case.year or plan.opening_cash != case.opening_cash:
        raise ValueError("Combined IRA contributions must share the year and opening cash.")
    validate_identity(case, plan)
    validate_records(case)
    validate_tax_context(case)


def validate_identity(case, plan):
    original = {a.id: a.model_dump(exclude={"product"}) for a in case.accounts}
    if {a.id: a.model_dump() for a in plan.accounts} != original:
        raise ValueError("Combined contribution accounts must match the ordinary IRA opening book.")
    expected = {p.id: p.birth_date for p in case.owners}
    if {p.id: p.birth_date for p in plan.contributors} != expected:
        raise ValueError("Contribution owners and births must match the IRA pools.")


def validate_records(case):
    plan = case.contributions
    if any(o.kind not in {"traditional_ira", "roth_ira"} for o in plan.orders):
        raise ValueError("Only ordinary IRA contributions belong in the combined IRA book.")
    records = [*case.orders, *case.returns, *case.incoming_rollovers, *plan.orders, *plan.receipts]
    if len({r.id for r in records}) != len(records):
        raise ValueError("Combined IRA cash and return events need unique IDs.")


def validate_tax_context(case):
    annual = case.annual_tax_case
    if annual is None:
        return
    if annual.filing.status != case.contributions.filing:
        raise ValueError("Contribution eligibility and annual tax filing status must match.")
    if annual.federal_income.deductible_ira_contributions:
        raise ValueError("Remove manual IRA deductions when modeling funded contributions.")
    if annual.federal_income.social_security:
        raise ValueError(
            "Combined IRA contribution/benefit deduction worksheets are not yet supported."
        )
    if annual.federal_income.allowed_passive_income < 0:
        raise ValueError("AGI-dependent passive losses require another IRA MAGI adapter.")
    if annual.federal_income.ira_distributions:
        raise ValueError("Complete IRA pools cannot duplicate manual annual IRA income.")
