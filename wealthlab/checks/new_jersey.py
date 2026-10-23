"""Focused NJ mapping spike, not a complete NJ return or reusable tax interface."""


def category_income(wages: float, dispositions: list[float]) -> float:
    """NJ-DOP nets transactions within its category; losses cannot reduce wages."""
    return wages + max(0.0, sum(dispositions))


def joint_schedule(taxable_income: float) -> float:
    """2025 NJ-1040 p63 Table B, only the tested $150k-$500k interval."""
    if not 150_000 <= taxable_income <= 500_000:
        raise ValueError("This mapping spike supports only taxable income $150k-$500k.")
    return taxable_income * 0.0637 - 4_042.50


def cases() -> list[tuple[str, float, float]]:
    return [
        ("NJ 2025 joint schedule, $200k taxable", joint_schedule(200_000), 8_697.50),
        ("NJ disposition losses cannot offset wages", category_income(200_000, [-30_000]), 200_000),
        (
            "NJ dispositions net within category",
            category_income(200_000, [50_000, -30_000]),
            220_000,
        ),
    ]
