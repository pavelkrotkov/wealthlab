"""HSA cash movements precede IRA elections, then current taxes and spending."""


def receipt_hook(ira, hsa):
    hooks = [book.after_receipts for book in (hsa, ira) if hasattr(book, "after_receipts")]
    if not hooks:
        return None

    def apply(wallet, start, end):
        for hook in hooks:
            yield from hook(wallet, start, end)

    return apply
