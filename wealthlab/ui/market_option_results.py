"""Model marks do not imply historical option performance or complete concentration coverage."""

import json

import streamlit as st

from wealthlab.ui.household_options import display as household_results
from wealthlab.ui.product_selections import select as saved_select


def display(result, index, rows):
    if not result["binding"].get("options"):
        return
    st.subheader("Options on identical realized market paths")
    st.caption(
        "Counterfactual QuantLib marks use fixed implied volatility, rates and pricing yields; "
        "Underlying return volatility is separate. No historical option quotes, "
        "exercise predictions, intramonth execution or roll quotes are manufactured. "
        "Constraints include every supplied mark. Derivative-adjusted "
        "issuer concentration is unmeasured; one protected leg cannot ensure a portfolio floor."
    )
    outcome = next(item for item in result["outcomes"] if item["path"] == index)
    st.write({key: value for key, value in outcome.items() if key.startswith("option_")})
    household_results(rows)
    with st.expander("Realized option mark assumptions and all observed collateral checks"):
        st.json(
            json.dumps(
                dict(
                    binding=result["binding"]["options"],
                    marks=rows[-1].get("option_mark_audit", []),
                ),
                default=str,
            )
        )


def selection():
    """Keep the option policy when another account workbench temporarily unmounts it."""
    choices = ["Covered call", "Collar", "Four-leg synthetic exposure"]
    return saved_select(
        "Option market example",
        choices,
        "option_market_strategy",
        default=choices[-1],
    )
