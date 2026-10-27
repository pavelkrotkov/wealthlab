"""Independent account variants retain shared opening capital and qualified medical history."""

from optimization_account_cases import case

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.retirement.hsa_investment_example import synthetic as hsa_investments
from wealthlab.retirement.workplace_roth_example import synthetic as roth_household


def invested():
    data = case().model_dump(mode="json")
    investment = hsa_investments().model_dump(mode="json")
    investment.update(marks=[], cash_targets=[])
    investment["case"].update(
        end="2027-12-31",
        trades=[],
        distributions=[],
        fee_schedules=[],
        closing_prices=dict(fund="100"),
    )
    investment["case"]["accounts"][0].update(id="cash_hsa", cash="0")
    investment["case"]["lots"][0].update(
        account_id="cash_hsa", federal_basis="10000", nj_basis="10000"
    )
    investment["funding_sources"][0].update(account_id="cash_hsa", commission="1")
    data["household"]["hsa_plan"].update(
        investments=investment,
        cash_only_accounts_and_complete_context_confirmed=False,
        cash_accounts_outside_investment_book_confirmed=True,
        investment_income_excluded_from_other_inputs_confirmed=True,
    )
    data["binding"].update(
        hsa_securities=[dict(security_id="fund", factor="equities", nj_cash_character="dividends")],
        replace_hsa_observations_confirmed=True,
    )
    return PolicySearch.model_validate(data)


def roth():
    data = case().model_dump(mode="json")
    household = data["household"]
    for account in household["accounts"]:
        if account["id"] == "work_pretax":
            account.update(id="work_roth", wrapper="roth")
    plan = roth_household().workplace_plan
    household["workplace_plan"].update(
        products=dict(work_roth="roth_401k"),
        cash_withdrawals=None,
        roth_cash_withdrawals=plan.roth_cash_withdrawals.model_dump(mode="json"),
    )
    for choice in data["dimensions"][-1]["choices"]:
        order = choice.pop("workplace_cash_orders")[0]
        choice["workplace_roth_orders"] = [dict(order, source="work_roth")]
    return PolicySearch.model_validate(data)
