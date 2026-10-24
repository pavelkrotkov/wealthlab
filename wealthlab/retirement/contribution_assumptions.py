"""A forward scenario may freeze supported limits; it cannot label them future law.

The actual calendar year still determines age, event dates and coverage.
Only dollar limits, phaseout bands and the wage threshold use the rule base.
"""

from typing import Literal

RuleMode = Literal["published", "freeze_2026_assumption"]


def rule_year(case):
    if case.rule_mode == "freeze_2026_assumption":
        if case.year < 2026:
            raise ValueError("Frozen 2026 contribution rules cannot apply before 2026.")
        return 2026
    if case.year not in {2025, 2026}:
        raise ValueError(
            "Published contribution rules here cover 2025/2026 only; "
            "select an explicit future assumption."
        )
    return case.year
