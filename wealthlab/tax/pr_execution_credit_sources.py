"""Exclude section 933 income from FTC limits while retaining raw payroll facts.

The same stable person/year/source must reconcile between independently typed
PR and FTC inputs. PR-excluded taxes cannot become excess carry vintages. A
source cannot become foreign merely by changing a country label: unresolved
third-country treaty resourcing requires another expressly supported profile.
"""

from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_residence import excluded
from wealthlab.tax.pr_source_facts import SourceIncome


def included(case):
    context = case.annual.pr_federal
    year = case.annual.policy.year
    rows = [r for r in case.income if r.value.date.year == year]
    if context is None:
        return rows
    prepared, statuses = prepare(case.annual)
    sources = {(r.owner_id, r.id): r.income for r in context.sources}
    result = []
    for row in rows:
        source = validate_link(row, sources.get((row.owner_id, row.id)))
        if not excluded(source, getattr(prepared, source.owner), statuses[source.owner], year):
            result.append(row)
    return result


def validate_link(row, source: SourceIncome | None) -> SourceIncome:
    if source is None:
        raise ValueError("Every FTC source needs the same stable PR person/year/source identity.")
    if (row.value.date, row.value.dollars(), row.kind) != (
        source.received,
        source.federal_amount,
        source.kind,
    ):
        raise ValueError("FTC and prepared PR source facts disagree on date, amount or character.")
    country = "PR" if source.federal_source == "PR" else "US"
    if row.country != country:
        raise ValueError(
            "Prepared PR/US source context cannot infer third-country treaty resourcing."
        )
    return source


def excluded_tax_reasons(case):
    if case.annual.pr_federal is None:
        return []
    permitted = {r.id for r in included(case)}
    records = {r.id: r for r in case.tax_cash}
    for payment in case.tax_cash:
        original = records[payment.reverses_id] if payment.kind == "refund" else payment
        if original.value.date.year != case.annual.policy.year:
            continue
        if positive_excluded_tax(payment, permitted):
            return ["PR-excluded or historical unverified income cannot generate US FTC/carry."]
    return []


def household_annual(annual):
    if annual.pr_federal is None:
        return annual
    from wealthlab.tax.foreign_tax_sources import key

    context = annual.pr_federal
    sources = [
        r.model_copy(update=dict(id=key(r.owner_id, r.income.received.year, r.id)))
        for r in context.sources
    ]
    values = dict(sources=sources)
    if context.gain_profile is not None:
        gains = [
            g.model_copy(update=dict(source_id=key(g.owner_id, annual.policy.year, g.source_id)))
            for g in context.gain_profile.gains
        ]
        values["gain_profile"] = context.gain_profile.model_copy(update=dict(gains=gains))
    return annual.model_copy(update=dict(pr_federal=context.model_copy(update=values)))


def positive_excluded_tax(payment, permitted):
    return (
        payment.creditable_native
        and payment.eligibility == "allowed"
        and any(identity not in permitted for identity in payment.income_ids)
    )


def extra_source_fields(case):
    context = case.annual.pr_federal
    if context is not None and context.gain_profile is not None:
        return {"long_term"}
    if any(
        r.kind == "long_term" and r.value.date.year == case.annual.policy.year for r in case.income
    ):
        raise ValueError("Dated capital-source rows require the native PR gain profile.")
    return set()
