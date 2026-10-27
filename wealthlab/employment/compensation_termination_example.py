"""Original synthetic conditional termination with actual cash and independent recognition."""

from wealthlab.employment.compensation_example import synthetic
from wealthlab.household.scenario import Scenario


def terminated(election="cash"):
    data = synthetic().model_dump(mode="json")
    plan = data["compensation_plan"]
    plan["tranches"][0]["liquid_from"] = data["start"]
    base = dict(tranche="award", provenance="illustration", date=data["start"])
    plan["events"] = [
        dict(
            base,
            id="redeem",
            sequence=0,
            kind="distribution",
            amount="20000",
            bucket="vested",
            purpose="ordinary",
            election=election,
        ),
        dict(base, id="forfeit", sequence=1, kind="forfeit", amount=None),
        dict(
            base,
            id="exit_tax",
            sequence=2,
            kind="allocation",
            federal=dict(allowed_passive_income="20000"),
            new_jersey=dict(business=dict(partnership="20000")),
        ),
        dict(
            base,
            id="termination",
            sequence=3,
            kind="termination",
            source_reference="Original synthetic termination worksheet; no actual contract claim",
            source_date=data["start"],
            contract_terminated=True,
            remaining_units="0",
            unit_label="Supplied synthetic award interests",
            remaining_deferred_value="0",
            remaining_cash_due="0",
            no_future_rights=True,
            no_future_contract_obligations=True,
            exit_tax_recognition_supplied=True,
        ),
    ]
    return Scenario.model_validate(data)
