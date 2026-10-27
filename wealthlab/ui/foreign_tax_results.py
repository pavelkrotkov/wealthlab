"""Show foreign liabilities, paid tax and credit uncertainty beside domestic results."""

import streamlit as st


def display(rows):
    if "foreign_tax_positions" not in rows[-1]:
        return
    st.subheader("Foreign tax cash and independently marked claims")
    a, b, c = st.columns(3)
    a.metric(
        "Foreign tax / fees actually paid", f"${sum(r['foreign_tax_paid'] for r in rows):,.2f}"
    )
    b.metric(
        "Foreign refunds actually received",
        f"${sum(r['foreign_tax_refund_received'] for r in rows):,.2f}",
    )
    c.metric("Ending net foreign tax payable", f"${rows[-1]['foreign_tax_position']:,.2f}")
    st.caption(
        "Positive positions are liabilities; negative positions are assessed refund claims. "
        "Current FX marks are valuation assumptions, not additional cash or US credits. "
        "Domestic income tax, payroll and NJ are reported separately above."
    )
    warnings(rows)
    st.dataframe(rows[-1]["foreign_tax_positions"], hide_index=True)
    st.dataframe(
        [record for row in rows for record in row["foreign_tax_cash_records"]], hide_index=True
    )
    with st.expander("US foreign-credit source, basket and original-vintage audit"):
        st.json(rows[-1]["foreign_tax_credit"])


def warnings(rows):
    for reason in sorted({reason for row in rows for reason in row["foreign_tax_unresolved"]}):
        st.warning(reason)
