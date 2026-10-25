"""Mixed-funds stock sales retain ordinary basis and the original investment clock.

The optional ten-year election is used only for appreciated qualifying stock;
nonqualifying shares retain cost basis. A supplied NJ profile may restrict a
federal benefit, but cannot grant a ten-year election denied federally.
"""

from wealthlab.household.calendar import money
from wealthlab.portfolio.disposal import is_long
from wealthlab.products.long_short_book import ZERO
from wealthlab.products.qoz_tax import event


def exit_event(tax, nav, proceeds, when, plan):
    values = {}
    for jurisdiction, book in tax["jurisdictions"].items():
        fmv = money(nav * book["elected"] / tax["funded"])
        step = elects_fmv(tax, book, when, plan, jurisdiction)
        if step:
            book["basis"] = max(book["basis"], fmv)
        basis = book["basis"] + book["ordinary_basis"]
        values[jurisdiction] = proceeds - basis
        tax["log"].append(
            dict(
                date=when.isoformat(),
                jurisdiction=jurisdiction,
                event="full_stock_sale",
                basis=basis,
                proceeds=proceeds,
                ten_year_election=step,
                gain=values[jurisdiction],
            )
        )
        book.update(basis=ZERO, ordinary_basis=ZERO)
    character = "long_term" if is_long(tax["invested"], when) else "short_term"
    return event(
        when,
        "QOZ full stock-interest sale; settlement cash separately dated",
        federal=values["federal"],
        nj=values["new_jersey"],
        character=character,
    )


def elects_fmv(tax, book, when, plan, jurisdiction):
    permitted = jurisdiction == "federal" or plan.federal == "allowed"
    if not (permitted and getattr(plan, jurisdiction) == "allowed" and book["elected"]):
        return False
    invested = tax["invested"]
    if when < invested.replace(year=invested.year + 10):
        return False
    if invested.year <= 2026 and when.year > 2047:
        raise ValueError("Legacy post-2047 QOF-election eligibility requires another profile.")
    return True
