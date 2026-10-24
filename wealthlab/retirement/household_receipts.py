"""Required sleeve cash precedes optional HSA/529/IRA deposits, then current taxes/spending."""


def receipt_hook(ira, hsa, education=None, products=None):
    hooks = [
        book.after_receipts
        for book in (products, hsa, education, ira)
        if hasattr(book, "after_receipts")
    ]
    if not hooks:
        return None

    def apply(wallet, start, end):
        for hook in hooks:
            yield from hook(wallet, start, end)

    return apply


def required(education, hsa):
    return (education.cash_need if education else 0) + (hsa.medical.owed if hsa else 0)
