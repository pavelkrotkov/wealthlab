"""Country-recognized tax changes one assessment position without another bank debit."""

import pytest
from foreign_tax_cases import withheld

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.foreign_credit_example import synthetic as credit_example
from wealthlab.tax.foreign_tax_example import synthetic


def test_usd_payer_cash_and_recognized_eur_levy_do_not_create_a_second_debit():
    data = withheld()
    item = data["foreign_tax_plan"]["source_withholding"][0]
    record = item["record"]
    record["tax_value"] = record["value"]
    record["value"] = amount("2025-10-15", 11000)
    record["creditable_native"] = "9000"
    item.update(
        recognized_tax_native="9000",
        recognition_source="9000EUR levy,1000EUR noncreditable penalty",
    )
    row = project(Scenario.model_validate(data))[0]
    position = row["foreign_tax_positions"][0]
    cash = row["foreign_tax_cash_records"][0]
    assert row["closing_cash"] == 57470
    assert (position["actual_net_paid_native"], position["remaining_native"]) == (9000, 1000)
    assert row["foreign_tax_position"] == 1100
    assert (cash["currency"], cash["tax_currency"]) == ("USD", "EUR")
    assert cash["local_recognized_tax_native"] == 9000


def test_refund_cannot_reverse_more_local_tax_than_applied_even_if_gross_cash_cap_allows_it():
    data = synthetic().model_dump(mode="json")
    original = credit_example().tax_cash[0].model_dump(mode="json")
    original.update(id="opening", value=amount("2025-08-31", 10000, "EUR", "1.1"))
    refund = dict(
        original,
        id="old_refund",
        kind="refund",
        reverses_id="opening",
        value=amount("2025-09-15", 9500, "EUR", "1.1"),
        creditable_native="9500",
    )
    data["foreign_tax_plan"]["opening_payments"] = [
        dict(
            assessment_id="es_income_2025",
            source_income_year=2025,
            record=original,
            recognized_tax_native="9000",
            recognition_source="Applied levy excludes penalty",
        ),
        dict(
            assessment_id="es_income_2025",
            source_income_year=2025,
            record=refund,
            recognized_tax_native="9500",
            recognition_source="Deliberately excessive applied reversal",
        ),
    ]
    with pytest.raises(ValueError, match="original local tax"):
        project(Scenario.model_validate(data))


def test_country_recognition_cannot_exceed_actual_levy_or_omit_its_independent_evidence():
    for recognized, evidence in [("11000", "Excess deliberately supplied"), ("9000", "")]:
        data = withheld()
        data["foreign_tax_plan"]["source_withholding"][0].update(
            recognized_tax_native=recognized, recognition_source=evidence
        )
        with pytest.raises(ValueError, match=r"Recognized local tax|own supplied evidence"):
            project(Scenario.model_validate(data))
