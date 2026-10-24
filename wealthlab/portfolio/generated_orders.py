"""Reserve generated identifiers against all user orders, including future ones."""

from hashlib import sha256


def identity(book, prefix, suffix):
    candidate = prefix + "_" + suffix
    if len(candidate) > 80:
        candidate = sha256(candidate.encode("utf-8")).hexdigest()
    if candidate in book.allocated_ids:
        raise ValueError("Generated trade ID collides with an existing input: " + candidate)
    book.allocated_ids.add(candidate)
    return candidate
