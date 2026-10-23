"""Do not grant an ordinary fund loss when received distributions require special rules."""

from datetime import date

from wealthlab.portfolio.share_ranges import overlap


def validate_fund_losses(case, book):
    affected = {
        event.id
        for event in case.distributions
        if event.federal_character in {"long_term", "tax_exempt_interest"}
    }
    for sale in book.disposals:
        if not short_fund_loss(book, sale):
            continue
        if any(matched(sale, row, affected) for row in book.distributions):
            raise ValueError(
                "Short-held fund losses with capital-gain/exempt-interest distributions "
                "require special loss adjustments not yet implemented."
            )


def short_fund_loss(book, row):
    sold = date.fromisoformat(row["date"])
    return (
        book.accounts[row["account_id"]].wrapper == "taxable"
        and book.securities[row["security_id"]].kind == "etf"
        and row["federal_gross_gain"] < 0
        and (sold - row["acquired"]).days <= 184
    )


def matched(sale, row, affected):
    # Only actual entitlements on the sold shares count. Future distributions
    # and distributions earned by other purchases cannot affect this guard.
    return (
        row["distribution"] in affected
        and sale["purchase_order"] == row["purchase_order"]
        and overlap(sale["share_offset"], sale["quantity"], row["share_offset"], row["quantity"])
        > 0
    )
