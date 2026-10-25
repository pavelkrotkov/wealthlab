"""Report RMD failure amounts separately from unmet household spending cash.

An RMD is an asset transfer, so its missed amount is not another expense or
debt deducted from wealth. Its tax is a real liability; its missed requirement
still fails the policy even when ordinary spending and tax bills were funded.
"""

from decimal import Decimal

ZERO = Decimal(0)


def summary(rows):
    if "workplace_rmd_required" not in rows[-1]:
        return {}
    failures = failed_rows(rows)
    annual = {r["date"][:4]: r["workplace_rmd_required"] for r in rows}
    return dict(
        workplace_rmd_required_total=sum(annual.values(), ZERO),
        workplace_rmd_shortfall_total=sum((r["workplace_rmd_shortfall"] for r in rows), ZERO),
        workplace_rmd_excise_tax_total=sum((r["workplace_rmd_excise_tax"] for r in rows), ZERO),
        workplace_rmd_unresolved_terminal=(
            rows[-1]["workplace_rmd_unresolved_prior"] + rows[-1]["workplace_rmd_shortfall"]
        ),
        first_workplace_rmd_failure=failures[0]["date"] if failures else None,
    )


def failed_rows(rows):
    return [
        r
        for r in rows
        if r["workplace_rmd_shortfall"] > 0 or r["workplace_rmd_unresolved_prior"] > 0
    ]
