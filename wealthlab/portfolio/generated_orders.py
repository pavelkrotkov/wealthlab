"""Reserve generated identifiers against all user orders, including future ones."""


def identity(book, prefix, suffix):
    candidate = prefix[:55] + "_" + suffix
    if candidate in book.allocated_ids:
        raise ValueError("Generated trade ID collides with an existing input: " + candidate)
    book.allocated_ids.add(candidate)
    return candidate
