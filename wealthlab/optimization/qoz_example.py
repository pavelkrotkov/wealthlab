"""Use an original complete synthetic QOF contract with existing actual source shares.

No stock, basis or opening cash is added. The source sale executes on the same
realized path for all participation choices; finite profiles alter subscriptions.
Imported private scenarios retain their own source terms and observations.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset
from wealthlab.markets.qoz_example import binding
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import add_factor
from wealthlab.products.qoz_example import account, contract, economic_case


def extend(case):
    validate_starter(case)
    lot = source_lot(case.household)
    data = case.model_dump(mode="json")
    household = data["household"]
    household["accounts"].append(account("qoz", "taxable", "0"))
    scenario = Scenario.model_validate(household)
    plan = contract(scenario, economic_case(), scenario.start.year)
    plan.update(
        sale_requested=str(scenario.end - timedelta(days=1)),
        sale_not_before=str(scenario.end - timedelta(days=1)),
        settlement_months=0,
    )
    plan["calls"][0].update(source_trade_id="qoz_source_sale", source_lot_id=lot.id)
    household["qoz_plan"] = plan
    add_source_sale(household, lot, plan["calls"][0]["date"])
    data["qoz_offers"] = offers(plan, scenario.start)
    data["binding"]["qoz"] = binding().qoz.model_dump(mode="json")
    data["dimensions"].append(
        dict(
            id="qoz_participation",
            choices=[dict(id=o["id"], qoz_offer=o["id"]) for o in data["qoz_offers"]],
        )
    )
    for market in [
        data["training"],
        data["validation"],
        *(c["market"] for c in data["robustness"].values()),
    ]:
        add_factor(market, asset("qof_assets", "other", 0.06, 0.15, 0))
    return PolicySearch.model_validate(data)


def validate_starter(case):
    if not case.household.synthetic:
        raise ValueError("The QOZ starter only extends original synthetic examples.")
    if case.household.qoz_plan or case.qoz_offers:
        raise ValueError("The QOZ starter cannot replace existing supplied plans or offers.")
    if "qoz" in {a.id for a in case.household.accounts}:
        raise ValueError("The QOZ starter cannot replace an existing account.")
    if (case.household.start.month, case.household.start.day) != (1, 1):
        raise ValueError("This original QOZ starter requires its January opening calendar.")


def source_lot(household):
    if household.lot_plan is None:
        raise ValueError("The QOZ starter requires an existing linked direct-stock source.")
    book = household.lot_plan.case
    securities = {s.id: s for s in book.securities}
    accounts = {a.id: a for a in book.accounts}
    lot = next(
        (
            candidate
            for candidate in book.lots
            if securities[candidate.security_id].kind == "stock"
            and accounts[candidate.account_id].wrapper == "taxable"
        ),
        None,
    )
    if lot is None:
        raise ValueError("The QOZ starter needs an existing taxable direct-stock lot.")
    return lot


def add_source_sale(household, lot, when):
    policies = household["lot_plan"]["case"]["sale_policies"]
    policies.append(
        dict(
            id="qoz_source_sale",
            provenance="illustration",
            date=str(when),
            account_id=lot.account_id,
            security_id=lot.security_id,
            mode="sell_all",
            prices=household["lot_plan"]["opening_prices"],
            commission="0",
            selection="hifo",
        )
    )
    policies.sort(key=lambda p: str(p["date"]))


def offers(plan, when):
    half = dict(plan, calls=[dict(c, amount=str(Decimal(c["amount"]) / 2)) for c in plan["calls"]])
    reference = dict(
        plan, mode="liquid_reference", federal="denied", new_jersey="denied", settlement_months=0
    )
    return [
        offer(name, p, when)
        for name, p in (
            ("no_entry", None),
            ("half", half),
            ("full", plan),
            ("reference", reference),
        )
    ]


def offer(identity, plan, when):
    return dict(
        id=identity,
        provenance="illustration",
        plan=plan,
        source="Original complete hypothetical QOF profiles; no actual sponsor or legal terms",
        source_date=str(when),
        complete_cash_tax_and_terms_confirmed=True,
        profile_valid_for_all_candidate_income_and_paths_confirmed=True,
        declined_no_prior_interest_or_obligations_confirmed=plan is None,
    )
