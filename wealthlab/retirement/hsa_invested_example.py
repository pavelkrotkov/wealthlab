"""Original synthetic provider bills funded by actual HSA sales and shared receipts."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_investment_example import synthetic as invested
from wealthlab.retirement.medical_bill_example import synthetic as medical


def synthetic():
    data = medical().model_dump(mode="json")
    data["name"] = "Synthetic invested HSA with actual medical funding"
    data["end"] = "2027-01-01"
    data["accounts"][1].update(id="hsa", balance="10100")
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["tax_plan"]["events"] = []
    plan = data["hsa_plan"]
    plan["years"] = plan["years"][:1]
    plan.update(
        investments=invested().model_dump(mode="json"),
        cash_only_accounts_and_complete_context_confirmed=False,
        cash_accounts_outside_investment_book_confirmed=True,
        investment_income_excluded_from_other_inputs_confirmed=True,
        contributions=[],
        withdrawals=[],
    )
    plan["medical_bills"][0].update(hsa_source="hsa")
    # No supplied trades: provider requests own actual sales. Earlier earned
    # dividends remain cash/receivables under their original entitlement dates.
    plan["investments"]["case"].update(trades=[])
    plan["investments"]["cash_targets"] = []
    return Scenario.model_validate(data)
