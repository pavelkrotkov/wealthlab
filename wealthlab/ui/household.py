"""Local cash-flow scenarios with optional explicit annual tax assumptions."""

import streamlit as st
from pydantic import ValidationError

from wealthlab.employment.compensation_example import synthetic as compensation_example
from wealthlab.employment.compensation_stress import linked_shock
from wealthlab.employment.example import synthetic as employment_example
from wealthlab.household.advisory_advance_example import synthetic as advisory_example
from wealthlab.household.example import synthetic
from wealthlab.household.projection import project
from wealthlab.portfolio.household_example import synthetic as lot_example
from wealthlab.portfolio.january_example import synthetic as january_example
from wealthlab.portfolio.saving_example import synthetic as saving_example
from wealthlab.products.household_example import synthetic as sleeve_example
from wealthlab.products.life_household_example import synthetic as life_example
from wealthlab.products.option_household_example import synthetic as option_example
from wealthlab.retirement.education_household_example import synthetic as education_example
from wealthlab.retirement.hsa_distribution_example import synthetic as hsa_distribution_example
from wealthlab.retirement.hsa_household_example import synthetic as hsa_example
from wealthlab.retirement.hsa_invested_example import synthetic as hsa_invested_example
from wealthlab.retirement.hsa_payroll_example import synthetic as hsa_payroll_example
from wealthlab.retirement.ira_deposit_household_example import synthetic as ira_deposit_example
from wealthlab.retirement.ira_household_example import synthetic as ira_example
from wealthlab.retirement.medical_bill_example import synthetic as medical_example
from wealthlab.retirement.medicare_household_example import synthetic as medicare_example
from wealthlab.retirement.social_household_example import synthetic as benefit_example
from wealthlab.retirement.social_medicare_example import synthetic as withholding_example
from wealthlab.retirement.social_work_household_example import synthetic as work_benefit_example
from wealthlab.retirement.workplace_example import synthetic as workplace_example
from wealthlab.retirement.workplace_rmd_example import synthetic as workplace_rmd_example
from wealthlab.retirement.workplace_rollover_example import synthetic as rollover_example
from wealthlab.retirement.workplace_roth_example import synthetic as roth_plan_example
from wealthlab.retirement.workplace_withdrawal_example import synthetic as workplace_cash_example
from wealthlab.tax.foreign_tax_example import synthetic as foreign_tax_example
from wealthlab.tax.source_example import synthetic as source_example
from wealthlab.ui import editor, files, results
from wealthlab.ui.optional_dependencies import retirement_notice


def show():
    st.header("Household cash flow")
    retirement_notice()
    st.warning(
        "Enable household tax assumptions to include federal/NJ taxes. "
        "Without a tax plan, income is gross and taxes are omitted. "
        "Use Markets / Household funding for supported realized market execution; "
        "employer returns use dated events. "
        "Only explicitly permitted taxable accounts can be sold, "
        "using actual linked lots or entered proportional-basis assumptions. "
        "This screen does not yet establish retirement safety."
    )
    st.caption(
        "Payments use cash accounts in listed order: confirmed employee payroll elections, "
        "then sleeve collateral/recourse debt and optional HSA/529/IRA deposits after receipts "
        "and prior-tax arrears, "
        "then current tax withholding/settlement when enabled, "
        "debts, fees, essential, healthcare, "
        "mortgage, education, discretionary, then contributions. Unpaid debt interest "
        "accrues; fees remain owed; unmet spending is a shortfall. "
        "Only explicit sleeve margin terms create investment borrowing."
    )
    try:
        files.import_scenario()
        examples()
        scenario = st.session_state.setdefault("scenario", synthetic())
        updated = editor.editor(scenario)
        if updated is not None:
            rows = project(updated)
            st.session_state.update(scenario=updated, projection=rows)
            scenario = updated
        rows = st.session_state.get("projection")
        if rows is not None:
            results.display(scenario, rows)
            results.comparison(scenario)
        files.save_scenario(scenario)
    except (ValueError, ValidationError, OSError) as error:
        st.session_state.pop("projection", None)
        st.error(str(error))


def examples():
    choices = (
        ("Load synthetic observed advance advisory fees", advisory_example),
        ("Load synthetic foreign-tax household", foreign_tax_example),
        ("Load synthetic long-short household", sleeve_example),
        ("Load synthetic actual option household", option_example),
        ("Load synthetic whole-life household", life_example),
        ("Load synthetic scheduled liquid saving", saving_example),
        ("Load synthetic employee 401(k) household", workplace_example),
        ("Load synthetic 401(k) cash withdrawals", workplace_cash_example),
        ("Load synthetic separate-plan RMDs", workplace_rmd_example),
        ("Load synthetic direct plan rollover", rollover_example),
        ("Load synthetic designated Roth plan cash", roth_plan_example),
        ("Load synthetic Social Security household", benefit_example),
        ("Load synthetic Social Security with earned wages", work_benefit_example),
        ("Load synthetic employment household", employment_example),
        ("Load synthetic employer compensation household", compensation_example),
        ("Load synthetic linked employment and asset shock", linked_shock),
        ("Load synthetic IRA household", ira_example),
        ("Load synthetic IRA contribution household", ira_deposit_example),
        ("Load synthetic cash HSA household", hsa_example),
        ("Load synthetic payroll HSA household", hsa_payroll_example),
        ("Load synthetic pension with source withholding", source_example),
        ("Load synthetic invested HSA household", hsa_invested_example),
        ("Load synthetic nonqualified HSA household", hsa_distribution_example),
        ("Load synthetic current medical bills", medical_example),
        ("Load synthetic 529 tuition household", education_example),
        ("Load synthetic actual-lot funding household", lot_example),
        ("Load synthetic January wash reconciliation", january_example),
        ("Load synthetic Medicare household", medicare_example),
        ("Load synthetic Social Security with Medicare withholding", withholding_example),
    )
    for label, build in choices:
        if st.button(label):
            files.select_scenario(build())
            st.rerun()
