"""Original fee examples isolate actual equity, source identity and cash liabilities."""

from tests.qoz_market_cases import flat
from wealthlab.household.advisory_example import plan
from wealthlab.household.scenario import Scenario


def with_fee(case, account="brokerage", rate=".01", fixed="0"):
    payload = plan(case).model_dump(mode="json")
    schedule = payload["schedules"][0]
    schedule.update(
        covered=[dict(account_id=account, value_basis="modeled_net_account_equity")],
        tiers=[dict(upper_limit=None, annual_rate=rate)],
        fixed_per_period=fixed,
        day_count=360,
    )
    schedule["periods"] = [
        dict(
            accrual_start="2026-01-01",
            accrual_end="2026-01-31",
            valuation_date="2026-01-31",
            assessment_date="2026-01-31",
            payment_due_date="2026-01-31",
        )
    ]
    return case.model_copy(update=dict(advisory_fee_plan=type(plan(case)).model_validate(payload)))


def native(cash="5000", shocks=None):
    case, batch, binding = flat(shocks=shocks)
    data = case.model_dump(mode="json")
    data.update(qoz_plan=None, incomes=[])
    data["tax_plan"]["income_rules"] = []
    data["accounts"][0]["balance"] = cash
    data["lot_plan"]["case"]["sale_policies"] = []
    data["lot_plan"]["funding_sources"] = [
        dict(account_id="brokerage", security_id="stock", commission="0", selection="hifo")
    ]
    return Scenario.model_validate(data), batch, binding.model_copy(update=dict(qoz=None))


def plain(cash="5000", asset="100000"):
    case, _, _ = native(cash)
    data = case.model_dump(mode="json")
    data.update(end="2026-02-01", tax_plan=None, lot_plan=None)
    data["accounts"] = data["accounts"][:2]
    data["accounts"][1]["balance"] = asset
    return Scenario.model_validate(data)


def change(case, update):
    data = case.model_dump(mode="json")
    update(data["advisory_fee_plan"])
    return Scenario.model_validate(data)
