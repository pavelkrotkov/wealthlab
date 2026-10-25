"""Required sleeve cash precedes optional HSA/529/IRA deposits, then current taxes/spending."""

from wealthlab.household.advisory_household import optional_reservation


def receipt_hook(ira, hsa, education=None, products=None, options=None):
    first = hooks(options, products)
    optional = hooks(hsa, education, ira)
    if not first and not optional:
        return None

    def apply(wallet, start, end):
        for hook in first:
            yield from hook(wallet, start, end)
        with optional_reservation(products, wallet):
            for hook in optional:
                yield from hook(wallet, start, end)

    return apply


def required(education, hsa):
    return (education.cash_need if education else 0) + (hsa.medical.owed if hsa else 0)


def hooks(*books):
    return [book.after_receipts for book in books if hasattr(book, "after_receipts")]
