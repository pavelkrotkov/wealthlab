"""Synthetic saving/rebalancing menus preserve opening stock lots and a common market model.

The added bond factor is independent of equities/inflation in this illustration;
its invented historical marks/yields are zero. All assumptions remain editable,
and the unaltered default horizon/coverage constraints still apply.
"""

from wealthlab.markets.rebalance_example import policy
from wealthlab.optimization.inputs import PolicySearch


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The diversification starter only extends synthetic examples.")
    data = case.model_dump(mode="json")
    add_security(data)
    markets = [data["training"], data["validation"]]
    markets.extend(check["market"] for check in data["robustness"].values())
    for market in markets:
        add_factor(market)
    data["dimensions"].append(dict(id="diversification", choices=choices()))
    return PolicySearch.model_validate(data)


def add_security(data):
    plan = data["household"]["lot_plan"]
    plan["case"]["securities"].append(
        dict(
            id="bond",
            provenance="illustration",
            kind="etf",
            wash_group="bond",
            exposure_group="bond",
        )
    )
    plan["opening_prices"]["bond"] = plan["case"]["closing_prices"]["bond"] = "100"
    for mark in plan["monthly_marks"]:
        mark["prices"]["bond"] = "100"
    plan["funding_sources"].append(
        dict(
            account_id="brokerage",
            security_id="bond",
            selection="hifo",
            commission="1",
        )
    )
    exit_order = dict(plan["case"]["sale_policies"][0], id="bond_exit", security_id="bond")
    plan["case"]["sale_policies"].append(exit_order)
    for order in plan["case"]["sale_policies"]:
        order["prices"]["bond"] = "100"
    data["binding"]["securities"].append(
        dict(
            security_id="bond",
            factor="bonds",
            federal_cash_character="interest",
            nj_cash_character="interest",
        )
    )


def add_factor(market):
    market["assets"].append(
        dict(
            id="bonds",
            provenance="illustration",
            role="bond",
            expected_annual_mark_return=0.02,
            annual_volatility=0.06,
            annual_cash_yield=0.01,
        )
    )
    original = market["correlation"]
    # Existing equity/inflation dependence is unchanged; the new factor is independent.
    market["correlation"] = [
        [original[0][0], 0, original[0][1]],
        [0, 1, 0],
        [original[1][0], 0, original[1][1]],
    ]
    if market["historical"] is not None:
        history = market["historical"]
        history["source"] += "; added synthetic zero-return bond observations"
        for month in history["months"]:
            month["mark_returns"]["bonds"] = month["cash_yields"]["bonds"] = 0


def choices():
    rebalance = policy(0, "2026-01-31")
    rebalance.update(drift_band="0", max_sale_fraction="1")
    return [
        dict(id="hold_and_save", rebalances=[], savings=[saving(dict(stock="1"))]),
        dict(id="balanced", rebalances=[rebalance], savings=[saving(dict(stock=".5", bond=".5"))]),
        dict(id="completion", rebalances=[], savings=[saving(dict(bond="1"))]),
    ]


def saving(weights):
    return dict(
        id="save",
        provenance="illustration",
        date="2026-01-31",
        account_id="brokerage",
        amount="1000",
        target_weights=weights,
        commission_per_trade="1",
        minimum_cash="10000",
    )
