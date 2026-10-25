"""Every observed product obligation participates in joint feasibility.

Drilling calls and creditors can remain unpaid while ordinary bills are paid.
Their failure dates join option, sleeve and policy failures without adding a
second creditor amount to wealth or turning a required payment into spending.
"""

from wealthlab.markets.life_reporting import outcome as life_outcome

FIELDS = dict(
    margin_triggered="triggered",
    margin_unresolved="margin",
    negative_equity="negative",
    exit_blocked="blocked",
    constraints_failed="constraints",
)


def condition_dates(audit, key):
    return {item["date"] for item in audit if item.get(key)}


def negative_dates(audit):
    return {item["date"] for item in audit if item["wealth"] - item["outside_cash"] < 0}


def blocked_dates(audit):
    return {item["date"] for item in audit if item.get("phase") == "unwind_incomplete"}


def states(audit):
    result = dict(
        triggered=condition_dates(audit, "margin_called"),
        margin=condition_dates(audit, "collateral_shortfall"),
        negative=negative_dates(audit),
        blocked=blocked_dates(audit),
        execution=condition_dates(audit, "execution_failed"),
    )
    result["constraints"] = (
        result["margin"] | result["negative"] | result["blocked"] | result["execution"]
    )
    return result


def months(dates):
    return len({day[:7] for day in dates})


def combined(rows, options):
    result = {}
    for name, key in FIELDS.items():
        dates = {row["date"] for row in rows if row.get(f"sleeve_{name}")}
        result[name] = dates | options[key]
    return result


def outcome(rows, funded):
    options = states(rows[-1].get("option_mark_audit", []))
    products = combined(rows, options)
    life_failures, life = life_outcome(rows)
    products["constraints_failed"].update(life_failures)
    drilling = condition_dates(rows, "drilling_product_failure")
    products["constraints_failed"].update(drilling)
    failures = products["constraints_failed"]
    return dict(
        **{f"product_{key}_months": months(dates) for key, dates in products.items()},
        **life,
        product_feasible=not failures,
        joint_feasible=funded and not failures,
        first_product_failure=min(failures, default=None),
        drilling_feasible=not drilling,
        first_drilling_failure=min(drilling, default=None),
        drilling_failure_months=months(drilling),
        option_feasible=not options["constraints"],
        first_option_failure=min(options["constraints"], default=None),
        option_margin_failure_months=months(options["margin"]),
        option_negative_equity_months=months(options["negative"]),
        option_exit_blocked_months=months(options["blocked"]),
        option_execution_failure_months=months(options["execution"]),
    )
