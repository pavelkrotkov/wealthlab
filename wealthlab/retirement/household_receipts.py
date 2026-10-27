"""Required sleeve cash precedes optional HSA/529/IRA deposits, then current taxes/spending."""

from wealthlab.household.advisory_household import optional_reservation


def receipt_hook(ira, hsa, education=None, products=None, options=None, priority_hook=None):
    first = hooks(options, products)
    optional = hooks(hsa, education, ira)
    if not first and not optional:
        return None

    def apply(wallet, start, end):
        yield from apply_hooks(first, wallet, start, end, priority_hook)
        yield from apply_hooks(optional, wallet, start, end, priority_hook, products)
        if priority_hook is not None:
            priority_hook(wallet, start, end)

    return apply


def apply_hooks(callbacks, wallet, start, end, priority, products=None):
    for hook in callbacks:
        if priority is not None:
            priority(wallet, start, end)
        with optional_reservation(products, wallet):
            yield from hook(wallet, start, end)


def required(education, hsa):
    return (education.cash_need if education else 0) + (hsa.medical.owed if hsa else 0)


def hooks(*books):
    return [book.after_receipts for book in books if hasattr(book, "after_receipts")]
