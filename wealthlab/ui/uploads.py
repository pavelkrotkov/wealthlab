"""Bounded UTF-8 upload text for editable financial case forms and lot CSV imports."""

import streamlit as st

from wealthlab.household.storage import MAX_BYTES


def read(uploaded):
    raw = uploaded.getvalue()
    if len(raw) > MAX_BYTES:
        raise ValueError("Import exceeds the 2 MB limit.")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Use a UTF-8 text file, optionally with a byte-order mark.") from error


def source(uploaded, default):
    """Return actual editable text; invalid uploads do not reach a JSON editor."""
    if uploaded is None:
        return default
    try:
        return read(uploaded)
    except ValueError as error:
        st.error(str(error))
        return None
