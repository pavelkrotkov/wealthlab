"""HSA cash movements precede IRA elections, then current taxes and spending."""


def receipt_hook(ira, hsa, education=None):
    hooks = [
        book.after_receipts for book in (hsa, education, ira) if hasattr(book, "after_receipts")
    ]
    if not hooks:
        return None

    def apply(wallet, start, end):
        for hook in hooks:
            yield from hook(wallet, start, end)

    return apply
