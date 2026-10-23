"""Stable purchase/offset ranges follow a share through partial sales and wash splits."""

from decimal import Decimal


def record_sale(book, row, remaining):
    order, offset = book.share_order[remaining.id]
    row["purchase_order"] = order
    row["share_offset"] = offset
    book.share_order[remaining.id] = (order, offset + row["quantity"])


def overlap(left_start, left_qty, right_start, right_qty):
    return max(
        Decimal(0),
        min(left_start + left_qty, right_start + right_qty) - max(left_start, right_start),
    )
