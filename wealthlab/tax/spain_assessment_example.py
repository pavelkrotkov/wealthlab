"""Original independent-person/year cases and user-supplied remaining EUR schedules."""

from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan
from wealthlab.tax.spain_example import synthetic

SOURCE = "Original synthetic remaining schedule and assumed due date; no legal deadline inferred"


def annual(identity, person, year, region):
    data = synthetic(region).model_dump(mode="json")
    data.update(person_id=person, year=year, as_of=f"{year + 1}-07-31")
    if year != 2025:
        data["policy"] = "frozen_2025"
    for item in data["incomes"]:
        item["owner_id"] = person
        item["amount"]["date"] = f"{year}-12-31"
    for asset in data["assets"]:
        asset["owner_id"] = person
        asset["fiscal_value"]["date"] = f"{year}-12-31"
    return dict(id=identity, case=data)


def schedule(identity, assessment, kind, value, due="2027-07-31"):
    return dict(
        id=identity,
        assessment_id=assessment,
        tax_type=kind,
        due_date=due,
        amount_eur=str(value),
        source=SOURCE,
    )


def synthetic_plan():
    return SpainAssessmentPlan.model_validate(
        dict(
            synthetic=True,
            as_of="2027-07-31",
            annuals=[
                annual("person_a_2025", "synthetic_person", 2025, "castilla_la_mancha"),
                annual("person_a_2026", "synthetic_person", 2026, "castilla_la_mancha"),
                annual("person_b_2025", "synthetic_other", 2025, "madrid"),
            ],
            obligations=[
                schedule("a_2025_irpf_remaining", "person_a_2025", "irpf", "12787"),
                schedule("a_2025_ip_remaining", "person_a_2025", "wealth", "22470.87"),
                schedule("a_2025_sgf_remaining", "person_a_2025", "solidarity", "16181.60"),
            ],
        )
    )
