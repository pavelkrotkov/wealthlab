"""Required sleeve cash precedes optional HSA/529/IRA deposits, then current taxes/spending."""


def receipt_hook(ira, hsa, education=None, products=None, options=None, priority_hook=None):
    hooks = [
        book.after_receipts
        for book in (options, products, hsa, education, ira)
        if hasattr(book, "after_receipts")
    ]
    if not hooks:
        return None

    def apply(wallet, start, end):
        for hook in hooks:
            if priority_hook is not None:
                priority_hook(wallet, start, end)
            yield from hook(wallet, start, end)
        if priority_hook is not None:
            priority_hook(wallet, start, end)

    return apply


def required(education, hsa):
    return (education.cash_need if education else 0) + (hsa.medical.owed if hsa else 0)
