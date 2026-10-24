"""A starter must select only wage mappings the actual employment adapter supports."""

from wealthlab.employment.example import synthetic, template
from wealthlab.tax.projection_inputs import IncomeRule


def test_template_excludes_federal_wages_without_the_supported_nj_wage_mapping():
    case = synthetic()
    extra = case.incomes[0].model_copy(update=dict(id="other_wage", owner="person_b"))
    rule = IncomeRule(income_id=extra.id, federal="wages_spouse", new_jersey="none")
    tax = case.tax_plan.model_copy(update=dict(income_rules=[*case.tax_plan.income_rules, rule]))
    case = case.model_copy(update=dict(incomes=[*case.incomes, extra], tax_plan=tax))
    assert [p["income_ids"] for p in template(case)["paths"]] == [["salary"]]
