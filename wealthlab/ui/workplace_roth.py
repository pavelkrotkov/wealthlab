"""Roth contract cost, qualification and conditional state treatment remain visible beside cash."""

import streamlit as st


def display(rows):
    contracts = rows[-1].get("workplace_roth_contracts", [])
    if not contracts:
        return
    st.subheader("Designated Roth plan cash and cost")
    audit = rows[-1].get("workplace_roth_audit", [])
    st.metric("Designated Roth plan gross cash", f"${sum(r['gross'] for r in audit):,.2f}")
    st.caption(
        "Complete vested ordinary separated Roth401(k) contracts only. Subaccounts share one "
        "plan contract's cost pool; nonqualified payments recover cost pro-rata, not IRA "
        "contribution-first. Qualified payments also reduce cost pro-rata. Actual employee "
        "Roth deposits add cost and can start the participation clock. Federal qualification "
        "requires five taxable years and age59½; age55 separation only changes the additional "
        "tax, not income qualification. NJ follows the explicitly confirmed conditional "
        "same-qualification/pro-rata assumption with independent cost; this is not a verified "
        "NJ eligibility decision. Withholding applies to each jurisdiction's taxable portion. "
        "Unused cost after losses creates no modeled deduction or cash. Separated contracts "
        "cannot reopen through later deferrals. In-plan conversions, inherited/special "
        "distributions and direct Roth rollovers require other profiles."
    )
    st.dataframe(contracts, hide_index=True, width="stretch")
    if audit:
        labels = dict(
            date="Cash date",
            source="Roth plan source",
            gross="Gross Roth cash",
            net_cash="Net Roth cash",
            federal_qualified="Federal qualified",
            federal_basis_recovered="Federal basis recovered",
            nj_basis_recovered="NJ basis recovered",
            federal_taxable="Federal taxable",
            nj_taxable="Conditional NJ taxable",
            additional_tax="Additional federal tax",
            unfilled="Unfilled Roth request",
        )
        st.dataframe(
            [{label: row[key] for key, label in labels.items()} for row in audit],
            hide_index=True,
            width="stretch",
        )
