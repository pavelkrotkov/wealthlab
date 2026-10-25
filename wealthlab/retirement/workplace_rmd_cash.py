"""December catch-up uses only current permitted plan assets, never future prices."""

from decimal import Decimal
from types import SimpleNamespace

from wealthlab.retirement.account_liquidity import blocked
from wealthlab.retirement.workplace_rmd_validation import PREFIX


def automatic(book, wallet, locks, when):
    if book is None or when.month != 12 or not book.config.automatic_december_catchup:
        return
    for i, (gid, group) in enumerate(book.config.groups.items()):
        for j, source in enumerate(group.sources):
            if blocked(locks, source, when):
                continue
            amount = min(book.remaining(gid), wallet.balances[source])
            if amount > 0:
                yield SimpleNamespace(
                    id=f"{PREFIX}{when.year}_{i}_{j}",
                    date=when,
                    source=source,
                    amount=amount,
                    federal_withholding_rate=Decimal(".20"),
                    nj_withholding_rate=book.config.automatic_nj_withholding_rate,
                )
