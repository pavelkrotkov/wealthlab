"""Future release reaches its own annual return once and then uses ordinary capital carry rules."""

from conditional_loss_cases import allocation
from household_sleeve_cases import change, flat

from wealthlab.household.projection import project
from wealthlab.products.household_example import synthetic


def test_deferred_losses_release_in_the_next_year_without_a_duplicate_current_deduction():
    def configure(data):
        source = synthetic().model_dump(mode="json")
        data["end"] = "2028-01-01"
        data["tax_plan"]["cases"].append(source["tax_plan"]["cases"][1])
        sleeve = data["sleeve_plan"]["sleeves"][0]
        sleeve["observations"].extend(source["sleeve_plan"]["sleeves"][0]["observations"][12:])
        sleeve["allocations"] = [allocation("deferred", "deferred").model_dump(mode="json")]

    rows = project(change(flat(100000), configure))
    first, second = rows[11]["annual_tax"], rows[-1]["annual_tax"]
    assert (first["federal"]["agi"], second["federal"]["agi"]) == (50000, -3000)
    assert first["new_jersey"]["business_carry"] == []
    assert second["new_jersey"]["business_carry"][0].amount == 12000
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert rows[-1]["net_wealth"] == 200000 - first["total_liability"] - second["total_liability"]
