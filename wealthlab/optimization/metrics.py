"""Downside, paid taxes, spending cuts and observed concentration never disappear into a score."""

from statistics import median

from wealthlab.optimization.advisory_metrics import actual as advisory_metrics


def financial_metrics(result):
    outcomes = result["outcomes"]
    return dict(
        **tax_cash(result),
        maximum_drawdown=max(r["net_wealth_drawdown"] for r in outcomes),
        maximum_funding_shortfall=max(r["funding_shortfall"] for r in outcomes),
        median_discretionary_reduction=median(
            r["discretionary_spending_reduction"] for r in outcomes
        ),
        minimum_closing_cash=min(
            r["closing_cash"] for item in result["details"] for r in item["rows"]
        ),
        median_ending_property_equity=property_value(result, "net_equity"),
        median_ending_property_debt=property_value(result, "linked_debt_balance"),
        **issuer_metrics(outcomes),
        **advisory_metrics(result),
    )


def issuer_metrics(outcomes):
    return dict(
        issuer_concentration_complete=all(r["issuer_concentration_complete"] for r in outcomes),
        maximum_known_issuer_weight=max(
            (r["max_security_weight"] for r in outcomes if r["max_security_weight"] is not None),
            default=None,
        ),
    )


def foreign_cash(rows):
    return sum(row.get("foreign_tax_cash_outflow", 0) for row in rows)


def tax_cash(result):
    outcomes = result["outcomes"]
    return dict(
        median_net_cash_tax=median(
            r["net_cash_taxes_paid"] + foreign_cash(item["rows"])
            for r, item in zip(outcomes, result["details"], strict=True)
        ),
        median_domestic_net_cash_tax=median(r["net_cash_taxes_paid"] for r in outcomes),
        median_foreign_net_cash_tax=median(
            foreign_cash(item["rows"]) for item in result["details"]
        ),
    )


def property_value(result, key):
    return median(
        sum(p[key] for p in item["rows"][-1].get("property_positions", []))
        for item in result["details"]
    )
