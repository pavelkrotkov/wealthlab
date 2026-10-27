"""Synthetic full-year Spain facts bind three computed taxes to one household book."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_tax_example import synthetic
from wealthlab.tax.spain_assessment_plan import assessment
from wealthlab.tax.spain_example import amount, income
from wealthlab.tax.spain_example import synthetic as spanish
from wealthlab.tax.spain_execution_facts import SpainExecution

SOURCE = "Synthetic supplied same-year year-end tax schedule; no statutory deadline inferred"


def single():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "200000"
    data["accounts"].append(
        dict(data["accounts"][0], id="fiscal_property", wrapper="property", balance="8600000")
    )
    native = spanish().model_dump(mode="json")
    native.update(person_id="person_a", as_of="2025-12-31", long_held_gain_cap_exclusion_eur="0")
    native["incomes"] = [income("work_us", 50000, "general"), income("work_es", 50000, "general")]
    sources = {r["id"]: r for r in data["foreign_tax_plan"]["credit_profiles"][0]["income"]}
    for item in native["incomes"]:
        row = sources[item["id"]]
        item.update(owner_id="person_a", source_country=row["country"])
        item["amount"] = amount(50000, row["value"]["date"], "USD", "0.909090909091")
    for asset in native["assets"]:
        asset["owner_id"] = "person_a"
    # Independent Spanish statutory fiscal wealth is explicit; this fixture
    # verifies tax cash, not a claim that fiscal value equals US market value.
    native["cap_adjustment_source"] = SOURCE
    from wealthlab.tax.spain_assessment_inputs import SpanishAnnualAssessment

    annual = SpanishAnnualAssessment.model_validate(dict(id="person_a_2025", case=native))
    assessed = assessment(annual)["liabilities_eur"]
    foreign = data["foreign_tax_plan"]
    template_a, template_s = foreign["assessments"][0], foreign["schedules"][0]
    foreign.update(assessments=[], schedules=[])
    bindings, obligations = schedules(foreign, assessed, template_a, template_s, annual)
    execution = SpainExecution.model_validate(
        dict(
            assessments=dict(
                synthetic=True, as_of="2025-12-31", annuals=[annual], obligations=obligations
            ),
            bindings=bindings,
            source_links=[
                dict(annual_id=annual.id, spanish_income_id=name, us_income_id=name, source=SOURCE)
                for name in ("work_us", "work_es")
            ],
            us_source_and_spanish_recognition_reconciled_confirmed=True,
            source_reconciliation=SOURCE,
            spanish_foreign_credit_treatment="denied",
            credit_treatment_source=(
                "Conservative denied Spanish foreign-credit comparison; no eligibility inferred"
            ),
        )
    )
    return Scenario.model_validate(data), execution


def schedules(foreign, assessed, template_a, template_s, annual):
    bindings, obligations = [], []
    for tax, liability in assessed.items():
        identity = "es_2025_" + tax
        kind = "income" if tax == "irpf" else "wealth"
        foreign["assessments"].append(
            dict(
                template_a,
                id=identity,
                tax_type=kind,
                observed="2025-12-31",
                amount_native=str(liability),
            )
        )
        foreign["schedules"].append(
            dict(
                template_s,
                id=identity + "_due",
                assessment_id=identity,
                due_date="2025-12-31",
                requested_native=str(liability),
                creditable_fraction="0.5" if tax == "irpf" else "0",
                credit_eligibility="allowed" if tax == "irpf" else "denied",
            )
        )
        bindings.append(
            dict(annual_id=annual.id, tax_type=tax, foreign_assessment_id=identity, source=SOURCE)
        )
        obligations.append(
            dict(
                id=identity + "_due",
                assessment_id=annual.id,
                tax_type=tax,
                due_date="2025-12-31",
                amount_eur=str(liability),
                source=SOURCE,
            )
        )
    return bindings, obligations
