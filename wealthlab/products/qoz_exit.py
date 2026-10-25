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
    anniversary = tax["invested"].replace(year=tax["invested"].year + 10)
    for jurisdiction, book in tax["jurisdictions"].items():
        fmv = money(nav * book["elected"] / tax["funded"])
        treatment = getattr(plan, jurisdiction)
        permitted = jurisdiction == "federal" or plan.federal == "allowed"
        step = (
            treatment == "allowed" and permitted and when >= anniversary and bool(book["elected"])
        )
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
