"""HSA eligibility must agree with an enabled, confirmed Medicare coverage plan."""

from datetime import date


def validate_medicare(scenario, context):
    if scenario.medicare_plan is None:
        return
    coverage = scenario.medicare_plan.case.coverage
    for person in context.owners:
        for month in person.months:
            when = date(context.year, month.month, 1)
            enrolled = any(
                c.member == person.id
                and c.start <= when < c.end
                and any((c.part_a, c.part_b, c.part_d))
                for c in coverage
            )
            if month.medicare != enrolled:
                raise ValueError(
                    "HSA Medicare eligibility must agree with confirmed household enrollment."
                )
