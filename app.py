"""Local verification screen; household projection features are tracked separately."""

from wealthlab.runtime import configure

configure()

from importlib.util import find_spec  # noqa: E402

import streamlit as st  # noqa: E402


def checks():
    st.caption("Local financial scenario workbench · engine verification")
    st.info("The projection workbench is under construction. These are synthetic engine checks.")
    st.write("Verify the numerical foundations before entering household scenarios.")
    owl_available = find_spec("owlplanner") is not None
    retirement = st.checkbox(
        "Include the optional Owl retirement benchmark", disabled=not owl_available
    )
    if not owl_available:
        st.caption("Install the benchmarks extra to enable the Owl check.")
    if st.button("Run engine checks", type="primary"):
        from wealthlab.checks.report import run, versions

        with st.spinner("Running independent synthetic checks…"):
            results = run(retirement)
        st.dataframe(results, hide_index=True, width="stretch")
        st.json(versions())
        if all(row["passed"] for row in results):
            st.success("All selected engine checks passed.")
        else:
            st.error("An engine check failed. Do not use affected calculations.")
    st.page_link(
        "https://github.com/pavelkrotkov/wealthlab/issues", label="Implementation progress"
    )
    st.caption("GPL-3.0-or-later · Public source; private scenarios remain local.")


def main():
    st.set_page_config(page_title="Wealthlab", page_icon="📊", layout="wide")
    st.title("Wealthlab")
    page = st.sidebar.radio(
        "Workspace",
        [
            "Household",
            "Annual tax",
            "Cross-border",
            "Tax lots",
            "Retirement",
            "Markets",
            "Products",
            "Engine checks",
        ],
    )
    if page == "Household":
        from wealthlab.ui.household import show

        show()
    elif page == "Annual tax":
        from wealthlab.ui.tax import show

        show()
    elif page == "Cross-border":
        from wealthlab.ui.cross_border import show

        show()
    elif page == "Tax lots":
        from wealthlab.ui.lots import show

        show()
    elif page == "Retirement":
        from wealthlab.ui.retirement_workspace import show

        show()
    elif page == "Markets":
        from wealthlab.ui.markets import show

        show()
    elif page == "Products":
        from wealthlab.ui.products import show

        show()
    else:
        checks()


if __name__ == "__main__":
    main()
