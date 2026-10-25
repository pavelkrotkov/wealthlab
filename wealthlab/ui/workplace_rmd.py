"""Plan requirements, actual withdrawals and contingent shortfall tax stay visible."""

import streamlit as st


def display(rows):
    audit = rows[-1].get("workplace_rmd_audit", [])
    if not audit:
        return
    st.subheader("Required workplace withdrawals by plan")
    st.caption(
        "Subaccounts share their explicitly supplied plan group; separate plans cannot cover "
        "each other's requirement. Targets use prior December balances and confirmed beneficiary "
        "tables under frozen 2026 assumptions. The elected deadline is December 31, including "
        "a first "
        "RMD year. Optional December catch-up follows manual first-day withdrawals, before monthly "
        "returns. Required cash uses the separate entered noneligible withholding rate; eligible "
        "remainder keeps at least 20% federal withholding. Default shortfall excise is 25%; "
        "10% correction or allowed IRS waiver are contingent supplied tax outcomes, not "
        "established "
        "eligibility. Prior missed requirements remain unresolved and fail funding; actual later "
        "corrections and prior-return excise revisions need their own adapter. This "
        "profile requires "
        "separation by December 1 in each RMD year; current-employer delays are unfinished."
    )
    st.dataframe(
        [
            dict(
                Year=r["year"],
                Plan=r["plan"],
                Divisor=r["divisor"],
                Required=r["required"],
                Distributed=r["withdrawn"],
                Shortfall=r["shortfall"],
                **{"Excise tax": r["excise_tax"], "Excise case": r["excise_treatment"]},
            )
            for r in audit
        ],
        hide_index=True,
        width="stretch",
    )
    with st.expander("RMD plan groups, prior December balances and rule audit"):
        st.json(audit)
