"""Local financial workspaces and independent numerical verification."""

from wealthlab.runtime import configure

configure()

from importlib.util import find_spec  # noqa: E402

import streamlit as st  # noqa: E402


def checks():
    st.caption("Local financial scenario workbench · engine verification")
    st.info(
        "These synthetic checks verify numerical foundations. They do not validate personal inputs."
    )
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
            "Optimize",
            "Engine checks",
        ],
    )
    if page == "Engine checks":
        checks()
        return
    from importlib import import_module

    routes = {
        "Household": "household",
        "Annual tax": "tax",
        "Cross-border": "cross_border",
        "Tax lots": "lots",
        "Retirement": "retirement_workspace",
        "Markets": "markets",
        "Products": "products",
        "Optimize": "optimization",
    }
    import_module("wealthlab.ui." + routes[page]).show()


if __name__ == "__main__":
    main()
