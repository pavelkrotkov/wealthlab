"""Independent supplied partnership income, SE, QBI and AMT channels.

The calculator's e27200 is used only as a documented numerical QBI offset;
there is no actual farm-rental input in Wealthlab. e02000/e26270 preserve
income/NIIT identity while supplied eligible QBI replaces its automatic
assumption that all nonpassive partnership income qualifies for section 199A.
"""


def apply(data, income, scale):
    nonpassive = float(income.allowed_nonpassive_partnership_income) / scale
    data["e02000"] += nonpassive
    data["e26270"] = nonpassive
    data["k1bx14p"] = float(income.partnership_se_earnings_primary) / scale
    data["k1bx14s"] = float(income.partnership_se_earnings_spouse) / scale
    data["e27200"] = float(income.partnership_qbi_before_se_deduction) / scale - nonpassive
    data["PT_binc_w2_wages"] = float(income.partnership_qbi_w2_wages) / scale
    data["PT_ubia_property"] = float(income.partnership_qbi_qualified_property) / scale
    data["cmbtp"] = float(income.additional_amt_income) / scale


def report(income, values):
    return dict(
        supplied_nonpassive_income=income.allowed_nonpassive_partnership_income,
        supplied_se_earnings_primary=income.partnership_se_earnings_primary,
        supplied_se_earnings_spouse=income.partnership_se_earnings_spouse,
        supplied_qbi_before_se_deduction=income.partnership_qbi_before_se_deduction,
        supplied_amt_income=income.additional_amt_income,
        self_employment_tax=values["setax"],
        deductible_se_tax=values["c03260"],
        qbi_deduction=values["qbided"],
        scope="Prelimited supplied facts; no SE/QBI/AMT eligibility, QBI carry or IDC calculation",
        qbi_adapter="e27200 numerical QBI offset; no statutory farm-rental input",
    )
