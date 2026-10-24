"""Show realized bill forecasts separately from actual payment and liability outcomes."""

import streamlit as st

from wealthlab.ui.medical_bills import display as medical_results


def display(result, index, rows):
    detail = next(d for d in result["details"] if d["path"] == index)
    audit = detail.get("medical_bill_indexing", [])
    if not audit:
        return
    st.subheader("Medical costs under realized inflation")
    st.caption(
        "Selected input costs are declared at projection-start prices, not already-inflated bills. "
        "Costs use CPI observed before the due month. HSA elections either keep their "
        "nominal cap or their original bill share, capped by the actual bill. "
        "A forecast is not a paid receipt. Provider/cash payments and unpaid liabilities "
        "still come from the actual household ledger; cash-HSA assets retain their entered "
        "bank schedules and are not equity-factor investments."
    )
    st.dataframe(audit, hide_index=True, width="stretch")
    medical_results(rows)
