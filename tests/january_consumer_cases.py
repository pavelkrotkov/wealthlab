"""A December loss crosses published income thresholds in later consumer models."""

from wealthlab.portfolio.january_example import synthetic


def data(gain):
    result = synthetic().model_dump(mode="json")
    result["tax_plan"]["events"].append(
        dict(
            date="2026-03-01",
            description="Synthetic external allocation, not cash income",
            cash_received="0",
            federal=dict(long_term=str(gain)),
            new_jersey=dict(dispositions=str(gain)),
        )
    )
    result["lot_plan"]["case"]["trades"][0].update(quantity="400", price="40")
    result["lot_plan"]["case"]["nj_wash_treatment"] = "federal_rules"
    return result
