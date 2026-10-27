"""Original paid-year tax and a later refund span actual native closed returns.

The example assumes no additional US interest/penalties/compliance expense;
that is an editable conditional cost assumption, not a statutory exemption.
Known charges belong in the existing dated household expense schedules.
"""

from calendar import monthrange
from copy import deepcopy

from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import Payments
from wealthlab.tax.foreign_tax_example import synthetic

SOURCE = "Synthetic confirmed original-return reconciliation; ordinary paid method and explicit FX"


def synthetic_refund():
    data = synthetic().model_dump(mode="json")
    data["end"] = "2027-08-01"
    plan, foreign = data["tax_plan"], data["foreign_tax_plan"]
    plan["settlement_timing"] = "monthly_accrued"
    original = plan["cases"][0]
    profiles = [foreign["credit_profiles"][0]]
    for year in (2026, 2027):
        case = next_case(original, year)
        plan["cases"].append(case)
        profile = deepcopy(profiles[0])
        profile.update(annual=case, as_of=f"{year}-12-31")
        if year == 2026:
            for row in profile["income"]:
                row["value"]["date"] = "2026-06-30"
        else:
            row = deepcopy(profile["income"][0])
            row.update(id="refund_fx", kind="ordinary", country="US")
            row["value"].update(date="2027-06-30", amount="1500")
            profile["income"] = [row]
            profile["fx_income_treatment"] = "included_in_annual_facts"
        profiles.append(profile)
    foreign.update(
        credit_profiles=profiles,
        prior_return_redetermination="allowed",
        redetermination_source=(
            SOURCE + "; zero additional interest/penalties/costs are assumed in this example"
        ),
        redetermination_other_costs_complete_confirmed=True,
    )
    plan["events"] = [
        dict(
            date="2026-06-30",
            description="Actual earned wages",
            cash_received="100000",
            federal=dict(wages_primary="100000"),
            new_jersey=dict(wages="100000"),
        ),
        dict(
            date="2027-06-30",
            description="Receipt-year refund FX income; cash paid only by foreign book",
            cash_received="0",
            federal=dict(ordinary_noninvestment_income="1500"),
            new_jersey=dict(other="1500"),
        ),
    ]
    refund(foreign)
    foreign["quotes"] = quotes()
    saving(data)
    return Scenario.model_validate(data)


def next_case(original, year):
    case = deepcopy(original)
    case["policy"].update(year=year, mode="freeze_2025")
    case.update(nj_regime="freeze_2025", payments=Payments().model_dump(mode="json"))
    case["federal_income"]["wages_primary"] = "0"
    case["nj_income"]["wages"] = "0"
    case["filing"]["age_primary"] += year - 2025
    return case


def refund(foreign):
    record = dict(
        id="actual_refund",
        owner_id="person_a",
        country="ES",
        liability_year=2025,
        tax_type="income",
        kind="refund",
        basket="general",
        value=dict(
            date="2027-06-30", currency="EUR", amount="5000", usd_per_unit="1.40", fx_source=SOURCE
        ),
        creditable_native="5000",
        eligibility="allowed",
        included_income_confirmed=True,
        income_ids=["work_es"],
        source=SOURCE,
        reverses_id="es_installment_2025_10_31",
        fx_income_id="refund_fx",
    )
    foreign["refunds"] = [
        dict(assessment_id="es_income_2025", source_income_year=2025, record=record)
    ]
    foreign["revisions"] = [
        dict(
            assessment_id="es_income_2025",
            observed="2027-06-30",
            amount_native="5000",
            source=SOURCE,
        )
    ]


def quotes():
    return [
        dict(
            date=f"{year}-{month:02d}-{monthrange(year, month)[1]}",
            currency="EUR",
            usd_per_unit="1.40" if (year, month) >= (2027, 6) else "1.10",
            source=SOURCE,
        )
        for year in range(2025, 2028)
        for month in range(1, 13)
    ]


def saving(data):
    data["accounts"].append(
        dict(data["accounts"][0], id="saved_cash", wrapper="taxable", balance="0")
    )
    data["contributions"] = [
        dict(
            id="optional_save",
            provenance="illustration",
            destination="saved_cash",
            start="2025-10-01",
            end="2027-08-01",
            monthly_amount="10000000",
            currency="USD",
            annual_growth=0,
        )
    ]
