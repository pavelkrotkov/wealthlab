"""Monthly wages have actual source-event identities; future salary is not opening income."""

from calendar import monthrange

from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.jurisdiction_execution_example import native_pr


def monthly():
    data = native_pr().model_dump(mode="json")
    data.update(start="2025-09-01")
    annual = data["tax_plan"]["cases"][0]
    annual["federal_income"]["wages_primary"] = "80000"
    annual["nj_income"]["wages"] = "80000"
    annual["payments"]["employee_payroll_withheld"] = "6120"
    annual["pr_federal"]["primary"]["presence_days"] = 184
    template = annual["pr_federal"]["sources"][0]
    source_rows, credits = wage_sources(template)
    annual["pr_federal"]["sources"] = source_rows
    data["incomes"] = [
        dict(
            id="salary",
            owner="person_a",
            provenance="illustration",
            start="2025-09-01",
            end="2026-01-01",
            monthly_amount="10000",
            currency="USD",
            annual_growth=0,
            stop_at_retirement=False,
        )
    ]
    data["tax_plan"]["income_rules"] = [
        dict(income_id="salary", federal="wages_primary", new_jersey="wages")
    ]
    foreign = data["foreign_tax_plan"]
    foreign["quotes"].insert(0, dict(foreign["quotes"][0], date="2025-09-30"))
    foreign["credit_profiles"][0].update(annual=annual, income=credits)
    foreign["schedules"][0].update(
        income_ids=["wage_12"], creditable_fraction="0", credit_eligibility="denied"
    )
    return Scenario.model_validate(data)


def wage_sources(template):
    source_rows, credits = [], []
    for month in range(1, 13):
        when = f"2025-{month:02d}-{monthrange(2025, month)[1]}"
        country = "US" if month <= 6 else "PR"
        identity = f"wage_{month:02d}"
        row = dict(
            template,
            id=identity,
            income=dict(
                template["income"],
                received=when,
                federal_amount="10000",
                pr_amount="10000",
                federal_source=country,
                pr_source=country,
                us_government_wages=False,
            ),
        )
        source_rows.append(row)
        credits.append(
            dict(
                id=identity,
                owner_id="person_a",
                country=country,
                kind="wages",
                basket="general",
                value=amount(when, 10000),
                source_classification="Synthetic dated W2 services",
            )
        )
    return source_rows, credits
