"""Full-year country sources retain actual person/year/event dates and independent evidence.

A source in one jurisdiction is never created by copying a taxable aggregate
or by dropping an inconvenient worldwide receipt. Treaty source differences
need their own validated allocation before this ordinary bridge can execute.
"""


def validate_sources(scenario, execution):
    annuals = validate_links(execution)
    sources = us_sources(scenario.foreign_tax_plan)
    validate_worldwide(annuals, execution.source_links, sources)
    for link in execution.source_links:
        annual = annuals[link.annual_id]
        us = sources.get((annual.person_id, annual.year, link.us_income_id))
        if us is None:
            raise ValueError(
                "Spain source link must retain the actual US person and recognition year."
            )
        row = next(i for i in annual.incomes if i.id == link.spanish_income_id)
        validate_source_row(row, us)


def validate_source_row(row, us):
    if row.kind != "income":
        raise ValueError(
            "Native Spain cash sources require ordinary receipts; "
            "disposal FX/basis needs its own mapping."
        )
    if row.amount.date != us.value.date:
        raise ValueError("Linked ordinary source income must retain its actual recognition date.")
    if row.treaty_treatment != "none" or row.source_country != us.country:
        raise ValueError("Different country sources/treaty resourcing need a validated allocation.")
    if row.amount.currency == us.value.currency and row.amount.amount != us.value.amount:
        raise ValueError("Linked ordinary source cash amounts must reconcile independently.")


def validate_worldwide(annuals, links, sources):
    for identity, annual in annuals.items():
        supplied = {r.us_income_id for r in links if r.annual_id == identity}
        required = {key[2] for key in sources if key[:2] == (annual.person_id, annual.year)}
        if supplied != required:
            raise ValueError("Full-year Spain worldwide sources cannot omit known US income.")


def validate_links(execution):
    annuals = {a.id: a.case for a in execution.assessments.annuals}
    expected = {(a.id, i.id) for a in execution.assessments.annuals for i in a.case.incomes}
    links = {(r.annual_id, r.spanish_income_id) for r in execution.source_links}
    if links != expected or len(links) != len(execution.source_links):
        raise ValueError(
            "Every Spain recognized source needs its stable US person/year/source link."
        )
    return annuals


def us_sources(plan):
    sources = {
        (i.owner_id, i.value.date.year, i.id): i for p in plan.credit_profiles for i in p.income
    }
    return sources
