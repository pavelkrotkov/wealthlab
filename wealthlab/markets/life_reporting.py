"""Missing required policy cash or stated death protection cannot count as product safety.

Coverage is an independent supplied household requirement. The zero need in
an educational fixture is not inferred from policy value or an optimizer's
preferred surrender date. Failure settlement may preserve solvency without
fulfilling either the original premium requirement or the protection need.
"""


def outcome(rows):
    unpaid = {row["date"] for row in rows if row.get("life_payment_unfunded", 0) > 0}
    gap = {row["date"] for row in rows if row.get("life_protection_shortfall", 0) > 0}
    return unpaid | gap, dict(
        life_payment_failure_months=len(unpaid),
        life_protection_gap_months=len(gap),
        life_feasible=not (unpaid or gap),
    )
