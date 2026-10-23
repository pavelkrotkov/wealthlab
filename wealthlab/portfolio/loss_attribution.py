"""Explain current portfolio losses using an explicit, non-statutory allocation convention.

Tax law nets amounts, not source labels. Preserve short/long character, consume
current portfolio losses before external net losses and opening carry, and offset
portfolio gains before external net gains. The annual engine remains authoritative
for ending carry and liability. Attribution is not incremental tax benefit.
"""

from decimal import Decimal

CHARACTERS = ("short_term", "long_term")
USES = ("own_gain_offset", "external_gain_offset", "ordinary_consumed", "ending_carry")


def allocate(opening, book, distributions, result):
    year = opening.policy.year
    pools = {character: buckets(opening.federal_income, character) for character in CHARACTERS}
    for row in book.disposals:
        if int(row["date"][:4]) != year:
            continue
        amount = row["federal_recognized_gain"]
        pool = pools[row["federal_character"]]
        pool["gains"]["own"] += max(Decimal(0), amount)
        pool["losses"]["current"] += max(Decimal(0), -amount)
    for character, pool in pools.items():
        pool["gains"]["own"] += distributions.get(character, Decimal(0))
        pool["attribution"]["recognized_loss"] = pool["losses"]["current"]
        offset(pool, pool)
    offset(pools["short_term"], pools["long_term"])
    offset(pools["long_term"], pools["short_term"])
    for character, pool in pools.items():
        # The engine's carry worksheet preserves unused low-income deductions.
        # Use its result, not the headline annual deduction limit.
        ending = result["federal"][character.replace("_term", "_carry")]
        consumed = max(Decimal(0), sum(pool["losses"].values()) - ending)
        used = min(pool["losses"]["current"], consumed)
        pool["attribution"].update(
            ordinary_consumed=used, ending_carry=pool["losses"]["current"] - used
        )
    return {character: pool["attribution"] for character, pool in pools.items()}


def buckets(income, character):
    external = getattr(income, character)
    carry = getattr(income, character.replace("_term", "_carry"))
    return dict(
        gains=dict(own=Decimal(0), external=max(Decimal(0), external)),
        losses=dict(current=Decimal(0), external=max(Decimal(0), -external), carry=carry),
        attribution=dict(
            **dict.fromkeys(USES, Decimal(0)), external_net=external, opening_carry=carry
        ),
    )


def offset(loss_pool, gain_pool):
    """Dictionary insertion order is the documented source allocation convention."""
    for source, loss in loss_pool["losses"].items():
        for target, gain in gain_pool["gains"].items():
            used = min(loss, gain)
            loss -= used
            gain_pool["gains"][target] -= used
            if source == "current":
                loss_pool["attribution"][target + "_gain_offset"] += used
        loss_pool["losses"][source] = loss
