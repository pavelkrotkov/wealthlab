"""Public synthetic income receipts, foreign withholding and independently supplied FX gain."""

from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.foreign_credit_example import synthetic as credit_example
from wealthlab.tax.foreign_tax_example import synthetic


def withheld():
    data = synthetic().model_dump(mode="json")
    plan = data["foreign_tax_plan"]
    plan["schedules"] = []
    record = credit_example().model_dump(mode="json")["tax_cash"][0]
    record.update(id="foreign_withheld", kind="withholding", income_ids=["new_work"])
    record["value"]["date"] = "2025-10-15"
    plan["source_withholding"] = [
        dict(assessment_id="es_income_2025", source_income_year=2025, record=record)
    ]
    plan["credit_profiles"][0]["income"].append(
        source("new_work", "wages", 20000, "2025-10-15", "ES")
    )
    data["tax_plan"]["events"] = [
        dict(
            date="2025-10-15",
            description="Synthetic gross pay with foreign tax sent by payer",
            cash_received="9000",
            federal=dict(wages_primary="20000"),
            new_jersey=dict(wages="20000"),
            withholding=dict(
                gross_cash="20000",
                foreign_tax_withheld="11000",
                foreign_payment_id="foreign_withheld",
            ),
        )
    ]
    return data


def refunded():
    data = synthetic().model_dump(mode="json")
    plan = data["foreign_tax_plan"]
    plan["assessments"][0]["refund_claim_eligibility"] = "allowed"
    plan["revisions"] = [
        dict(
            assessment_id="es_income_2025",
            observed="2025-11-10",
            amount_native="9000",
            source="Synthetic confirmed original assessment reduction",
        )
    ]
    plan["quotes"][1]["usd_per_unit"] = "1.40"
    plan["quotes"][2]["usd_per_unit"] = "1.40"
    record = credit_example().model_dump(mode="json")["tax_cash"][0]
    record.update(
        id="actual_refund",
        kind="refund",
        reverses_id="es_installment_2025_10_31",
        value=amount("2025-12-15", 1000, "EUR", "1.40"),
        creditable_native="1000",
        fx_income_id="fx_gain",
    )
    plan["refunds"] = [dict(assessment_id="es_income_2025", source_income_year=2025, record=record)]
    plan["credit_profiles"][0]["fx_income_treatment"] = "included_in_annual_facts"
    plan["credit_profiles"][0]["income"].append(
        source("fx_gain", "ordinary", 300, "2025-12-15", "US")
    )
    data["tax_plan"]["events"] = [
        dict(
            date="2025-12-15",
            description="Independently classified refund currency income, no second receipt",
            cash_received="0",
            federal=dict(ordinary_noninvestment_income="300"),
            new_jersey=dict(other="300"),
        )
    ]
    return data


def source(identity, kind, dollars, when, country):
    return dict(
        id=identity,
        owner_id="person_a",
        country=country,
        kind=kind,
        basket="general",
        value=amount(when, dollars),
        source_classification="Synthetic independent recognized source classification",
    )


def multi_year():
    from calendar import monthrange
    from copy import deepcopy

    data = synthetic().model_dump(mode="json")
    data["end"] = "2027-01-01"
    plan = data["foreign_tax_plan"]
    future = deepcopy(plan["credit_profiles"][0])
    future["annual"]["policy"].update(year=2026, mode="freeze_2025")
    future["annual"]["nj_regime"] = "freeze_2025"
    future["annual"]["filing"]["age_primary"] = 41
    future["annual"]["federal_income"]["wages_primary"] = "0"
    future["annual"]["nj_income"]["wages"] = "0"
    future["annual"]["payments"] = {}
    future["as_of"] = "2026-12-31"
    for row in future["income"]:
        row["value"]["date"] = "2026-06-30"
    data["tax_plan"]["cases"].append(future["annual"])
    data["tax_plan"]["events"] = [
        dict(
            date="2026-06-30",
            description="Synthetic second-year covered wages",
            cash_received="100000",
            federal=dict(wages_primary="100000"),
            new_jersey=dict(wages="100000"),
        )
    ]
    plan["credit_profiles"].append(future)
    plan["quotes"].extend(
        dict(
            date=f"2026-{month:02d}-{monthrange(2026, month)[1]:02d}",
            currency="EUR",
            usd_per_unit="1.10",
            source="Synthetic second-year monthly quote",
        )
        for month in range(1, 13)
    )
    return data
