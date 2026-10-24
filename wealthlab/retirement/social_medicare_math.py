"""Current Part B changes MBC rounding; Part D IRMAA is collected afterwards.

The supported profile combines records into one payment per recipient, with
a sufficient active Part B record and no third-party payer or premium arrears.
Low Part B record exceptions require their own collection model rather than a
negative check or a guessed split between records.
"""

from decimal import ROUND_FLOOR, Decimal

from wealthlab.retirement.social_amounts import dollar

RECORDS = ("own_with_delayed_credits", "spousal_excess", "survivor_excess")


def calculate(row, bill, active):
    values = {key: row[key] for key in RECORDS}
    rounded = {key: dollar(value) for key, value in values.items()}
    bill = {} if bill is None else bill
    part_b = Decimal(bill.get("part_b", 0))
    part_d = Decimal(bill.get("d_irmaa", 0))
    apply_part_b(values, rounded, active, bill, part_b)
    gross = sum(rounded.values(), Decimal(0))
    available = gross - part_b
    d_withheld = part_d if available >= part_d else Decimal(0)
    return dict(
        gross_credited=gross,
        cash_received=gross - part_b - d_withheld,
        part_b_withheld=part_b,
        part_d_irmaa_withheld=d_withheld,
        part_d_irmaa_direct_bill=part_d - d_withheld,
        active_record=active,
        credited_records=rounded,
        change_from_no_premium_rounding=gross - row["issued_before_offsets"],
    )


def apply_part_b(values, rounded, active, bill, part_b):
    if bill.get("part_a", 0):
        raise ValueError("Premium Part A collection from benefits needs another supported profile.")
    if part_b:
        remainder = values[active] - part_b
        if remainder < 1:
            raise ValueError(
                "Part B requires a sufficient active benefit record with at least $1 remaining; "
                "low/combined-payment cases need additional collection rules."
            )
        rounded[active] = remainder.to_integral_value(rounding=ROUND_FLOOR) + part_b
