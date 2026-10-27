"""Separate purchase/sale FX prevents a net dollar gain from being translated once."""

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import amount, income, synthetic
from wealthlab.tax.spain_inputs import SpainCase


def test_gain_uses_separately_translated_sale_proceeds_and_acquisition_cost():
    data = synthetic().model_dump(mode="json")
    gain = income("foreign_disposal", 0, "savings")
    gain.pop("amount")
    gain.update(
        kind="disposal",
        proceeds=amount(10000, "2025-11-01", "USD", ".9"),
        acquisition=amount(8000, "2024-01-01", "USD", ".8"),
    )
    data["incomes"].append(gain)
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["assessment"]["bases"]["savings"] == 4600
    assert result["inputs"]["incomes"][-1]["acquisition"]["eur_per_unit"] == "0.8"
