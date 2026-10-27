"""Original fixed-country policy profiles reuse actual native jurisdiction inputs."""

from wealthlab.optimization.country_example import synthetic
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.tax.foreign_credit_example import amount as us_amount
from wealthlab.tax.spain_example import asset, income
from wealthlab.tax.spain_execution_example import single


def ready(wage="10000"):
    data = synthetic().model_dump(mode="json")
    data["targets"].update(target_age=50, reserve_years=0)
    data["household"]["incomes"][0]["monthly_amount"] = wage
    data["household"]["members"][0]["birth_date"] = "1974-01-01"
    annuals = [
        *data["household"]["tax_plan"]["cases"],
        *(p["annual"] for p in data["household"]["foreign_tax_plan"]["credit_profiles"]),
    ]
    for annual in annuals:
        annual["filing"]["age_primary"] = 51
    return PolicySearch.model_validate(data)


def spanish():
    case = ready().model_dump(mode="json")
    household, context = single()
    data, spain = household.model_dump(mode="json"), context.model_dump(mode="json")
    for unit in [
        *data["tax_plan"]["cases"],
        *(p["annual"] for p in data["foreign_tax_plan"]["credit_profiles"]),
    ]:
        unit["filing"]["age_primary"] = 51
    data["accounts"] = data["accounts"][:1]
    data["accounts"][0]["balance"] = "2000000"
    data["members"][0].update(birth_date="1974-01-01", retirement_date="2026-01-01")
    data["incomes"] = [dict(case["household"]["incomes"][0], start="2025-12-01")]
    data["tax_plan"]["income_rules"] = [
        dict(income_id="salary", federal="wages_primary", new_jersey="wages")
    ]
    annual = spain["assessments"]["annuals"][0]["case"]
    annual["assets"] = [dict(asset("cash", 200000, False), owner_id="person_a")]
    annual["assets"][0]["fiscal_value"].update(currency="USD", eur_per_unit="0.909090909091")
    row = income("future_wage", 10000, "general")
    row.update(owner_id="person_a", source_country="US")
    row["amount"].update(amount="10000", currency="USD", eur_per_unit="0.909090909091")
    annual["incomes"].append(row)
    spain["source_links"].append(
        dict(
            annual_id="person_a_2025",
            spanish_income_id="future_wage",
            us_income_id="future_wage",
            source="Original supplied December wage identity",
        )
    )
    for schedule in data["foreign_tax_plan"]["schedules"]:
        if schedule["assessment_id"] == "es_2025_irpf":
            schedule["requested_native"] = "200000"
        else:
            schedule["due_date"] = "2026-06-30"
            schedule["source"] = (
                "Synthetic future wealth-payment authorization; no deadline inferred"
            )
    for obligation in spain["assessments"]["obligations"]:
        if obligation["tax_type"] != "irpf":
            obligation["due_date"] = "2026-06-30"
    profile = data["foreign_tax_plan"]["credit_profiles"][0]
    profile["income"].append(
        dict(profile["income"][0], id="future_wage", value=us_amount("2025-12-31", 10000))
    )
    case.update(household=data)
    case["training"].update(start=data["start"], end=data["end"])
    case["validation"].update(start=data["start"], end=data["end"])
    case["country_context"].update(
        spain=spain,
        cash_sources=[dict(annual_id="person_a_2025", account_id="cash", asset_id="cash")],
        wage_sources=[dict(income_id="salary", source_id="future_wage", date="2025-12-31")],
    )
    return PolicySearch.model_validate(case)
